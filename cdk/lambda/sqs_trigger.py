import json
import os
import boto3

bedrock_agentcore = boto3.client('bedrock-agentcore')

def lambda_handler(event, context):
    agent_runtime_arn = os.environ['AGENT_RUNTIME_ARN']
    
    for record in event['Records']:
        message_body = record['body']
        
        response = bedrock_agentcore.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier='DEFAULT',
            payload=message_body.encode('utf-8')
        )
        
        print(f"Invoked AgentCore Runtime with message: {message_body}")
    
    return {'statusCode': 200}
