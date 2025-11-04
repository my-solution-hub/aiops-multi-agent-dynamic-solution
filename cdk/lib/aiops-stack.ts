import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as bedrockagentcore from 'aws-cdk-lib/aws-bedrockagentcore';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import { Construct } from 'constructs';
import * as fs from 'fs';
import * as path from 'path';

export class AIOpsStack extends cdk.Stack {
  public readonly investigationsTable: dynamodb.Table;
  public readonly agentPromptsTable: dynamodb.Table;
  public readonly feishuNotifier: lambda.Function;
  public readonly agentRole: iam.Role;
  public readonly userPool: cognito.UserPool;
  public readonly agentCoreGateway: bedrockagentcore.CfnGateway;
  public readonly agentRuntime: bedrockagentcore.CfnRuntime;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.investigationsTable = this.createInvestigationsTable();
    this.agentPromptsTable = this.createAgentPromptsTable();
    this.feishuNotifier = this.createFeishuNotifier();
    this.agentRole = this.createAgentRole();
    this.userPool = this.createUserPool();
    this.agentCoreGateway = this.createAgentCoreGateway();
    this.agentRuntime = this.createAgentRuntime();
    this.createConfigParameters();
    this.createOutputs();
  }

  private createInvestigationsTable(): dynamodb.Table {
    const table = new dynamodb.Table(this, 'InvestigationsTable', {
      tableName: 'aiops-investigations',
      partitionKey: { name: 'investigation_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'item_type', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    table.addGlobalSecondaryIndex({
      indexName: 'StatusIndex',
      partitionKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'created_at', type: dynamodb.AttributeType.STRING }
    });

    return table;
  }

  private createAgentPromptsTable(): dynamodb.Table {
    return new dynamodb.Table(this, 'AgentPromptsTable', {
      tableName: 'aiops-agent-prompts',
      partitionKey: { name: 'agent_name', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'version', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }

  private createFeishuNotifier(): lambda.Function {
    const configPath = path.join(__dirname, '../../config/.config');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const feishuWebhookUrl = config.notification_bot;

    return new lambda.Function(this, 'FeishuNotifier', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'feishu_notifier.lambda_handler',
      code: lambda.Code.fromAsset('lambda'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        FEISHU_WEBHOOK_URL: feishuWebhookUrl
      }
    });
  }

  private createAgentRole(): iam.Role {
    const role = new iam.Role(this, 'AIOpsAgentRole', {
      roleName: 'AIOpsAgentRole',
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('lambda.amazonaws.com'),
        new iam.ServicePrincipal('bedrock-agentcore.amazonaws.com')
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      inlinePolicies: {
        DynamoDBAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem',
                'dynamodb:Query', 'dynamodb:Scan'
              ],
              resources: [
                this.investigationsTable.tableArn,
                `${this.investigationsTable.tableArn}/index/*`,
                this.agentPromptsTable.tableArn
              ]
            })
          ]
        }),
        BedrockAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
              resources: ['*']
            })
          ]
        }),
        ECRAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'ecr:GetAuthorizationToken',
                'ecr:BatchGetImage',
                'ecr:GetDownloadUrlForLayer',
                'ecr:BatchCheckLayerAvailability'
              ],
              resources: ['*']
            })
          ]
        }),
        LambdaInvoke: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['lambda:InvokeFunction'],
              resources: ['*']
            })
          ]
        })
      }
    });

    return role;
  }

  private createUserPool(): cognito.UserPool {
    return new cognito.UserPool(this, 'AIOpsUserPool', {
      userPoolName: 'aiops-users',
      selfSignUpEnabled: true,
      signInAliases: { email: true },
      autoVerify: { email: true },
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }

  private createAgentCoreGateway(): bedrockagentcore.CfnGateway {
    const gateway = new bedrockagentcore.CfnGateway(this, 'AIOpsGateway', {
      name: 'aiops-notification-gateway',
      authorizerType: 'AWS_IAM',
      protocolType: 'MCP',
      roleArn: this.agentRole.roleArn,
      exceptionLevel: 'DEBUG',

      // authorizerConfiguration: {
      //   customJwtAuthorizer: {
      //     discoveryUrl: `https://cognito-idp.${this.region}.amazonaws.com/${this.userPool.userPoolId}/.well-known/openid-configuration`,
      //     allowedAudience: [this.userPool.userPoolId],
      //     allowedClients: [ "52vte516ehgb1inuvamt0pi9kv" ]
      //   }
      // }
    });

    new bedrockagentcore.CfnGatewayTarget(this, 'FeishuTarget', {
      gatewayIdentifier: gateway.attrGatewayIdentifier,
      name: 'feishu-notifier',
      targetConfiguration: {
        mcp: {
          lambda: {
            lambdaArn: this.feishuNotifier.functionArn,
            toolSchema: {
              inlinePayload: [{
                name: 'send_notification',
                description: 'Send notification to Feishu',
                inputSchema: {
                  type: 'object',
                  properties: {
                    message: {
                      type: 'string',
                      description: 'Notification message'
                    }
                  },
                  required: ['message']
                }
              }]
            }
          }
        }
      },
      credentialProviderConfigurations: [{
        credentialProviderType: 'GATEWAY_IAM_ROLE'
      }]
    });

    return gateway;
  }

  private createAgentRuntime(): bedrockagentcore.CfnRuntime {
    const imageUri = new cdk.CfnParameter(this, 'ImageUri', {
      type: 'String',
      description: 'ECR image URI (e.g., ACCOUNT.dkr.ecr.REGION.amazonaws.com/REPO:latest)'
    });

    return new bedrockagentcore.CfnRuntime(this, 'AIOpsRuntime', {
      agentRuntimeName: 'aiops_runtime',
      roleArn: this.agentRole.roleArn,
      agentRuntimeArtifact: {
        containerConfiguration: {
          containerUri: imageUri.valueAsString
        }
      },
      networkConfiguration: {
        networkMode: 'PUBLIC'
      }
    });
  }

  private createConfigParameters(): void {
    new ssm.StringParameter(this, 'ModelConfig', {
      parameterName: '/aiops/config/model',
      stringValue: JSON.stringify({
        default_model: {
          provider: 'bedrock',
          model_id: 'apac.amazon.nova-pro-v1:0',
          region: 'ap-southeast-1'
        }
      })
    });
  }

  private createOutputs(): void {
    new cdk.CfnOutput(this, 'InvestigationsTableName', {
      value: this.investigationsTable.tableName,
      description: 'DynamoDB table for investigations'
    });

    new cdk.CfnOutput(this, 'AgentPromptsTableName', {
      value: this.agentPromptsTable.tableName,
      description: 'DynamoDB table for agent prompts'
    });

    new cdk.CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
      description: 'Cognito User Pool ID for authentication'
    });

    new cdk.CfnOutput(this, 'FeishuNotifierArn', {
      value: this.feishuNotifier.functionArn,
      description: 'Feishu notifier Lambda function ARN'
    });

    new cdk.CfnOutput(this, 'AgentCoreGatewayArn', {
      value: this.agentCoreGateway.attrGatewayArn,
      description: 'AgentCore Gateway ARN for AIOps notifications'
    });

    new cdk.CfnOutput(this, 'AgentRuntimeArn', {
      value: this.agentRuntime.attrAgentRuntimeArn,
      description: 'AgentCore Runtime ARN for AIOps agent'
    });
  }
}
