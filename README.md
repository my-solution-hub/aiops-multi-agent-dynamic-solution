# AIOps Root Cause Analysis System

A multi-agent system for automated root cause analysis of AWS CloudWatch alarms using intelligent workflow generation and iterative investigation rounds.

## Architecture

### Overview

The system uses a **task-driven multi-agent architecture** with MCP (Model Context Protocol) gateways for tool integration and a feedback loop for adaptive workflow generation:

```
CloudWatch Alarm → Brain Agent → Tasks → Executor Agent → Specialized Agents → MCP Gateways → AWS Services
                        ↓                      ↓                                          ↓
                   Workflows            Update Context                          Domain-specific Tools
                        ↑                      ↓
                        ← ← ← ← ← ← ← (SQS: RE_EVALUATE)
```

### Message Flow

1. **ALARM → Brain Agent**
   - Process alarm text and generate investigation workflow
   - Initialize context in DynamoDB
   - Send SQS message (EXECUTION)

2. **EXECUTION → Executor Agent**
   - Execute next task with specialized agent
   - Update context with findings (prefixed by task_id)
   - Add timeline event
   - Send SQS message (RE_EVALUATE)

3. **RE_EVALUATE → Brain Agent**
   - Read accumulated context and findings
   - Assess confidence level
   - Adapt workflow: continue, add tasks, or conclude
   - Send SQS message (EXECUTION) if needed

### Core Components

1. **Brain Agent**: Alarm analyzer and workflow generator
   - Processes CloudWatch alarms
   - Generates investigation tasks with specific prompts
   - Assesses confidence and creates analysis reports

2. **Executor Agent**: Task orchestrator using Strands Graph
   - Receives tasks from Brain Agent
   - Creates specialized agents per task (with task-specific prompts)
   - Manages agent execution flow
   - Aggregates results back to Brain Agent

3. **Specialized Agents**: Domain experts with MCP tools
   - **LogsAgent**: CloudWatch Logs analysis (→ Observability Gateway)
   - **MetricsAgent**: CloudWatch Metrics analysis (→ Observability Gateway)
   - **TracesAgent**: X-Ray traces analysis (→ Observability Gateway)
   - **ResourceAgent**: AWS resource inspection (→ AWS Resources Gateway)
   - **NotificationAgent**: Alert delivery (→ Notification Gateway)

4. **MCP Gateways**: Tool providers (AgentCore Gateways)
   - Expose domain-specific tools via MCP protocol
   - Authenticated via AWS SigV4 (IAM)
   - Pre-configured per agent (static mapping)

### Gateway Organization

**Observability Gateway** (`observability-gateway`)
- CloudWatch Logs query tools
- CloudWatch Metrics query tools
- X-Ray traces query tools

**AWS Resources Gateway** (`resources-gateway`)
- EC2 describe/inspect tools
- RDS describe/inspect tools
- ELB describe/inspect tools
- Resource tagging tools

**Notification Gateway** (`notification-gateway`)
- Feishu notification tool
- Email notification (future)
- Slack notification (future)

### Agent-Gateway Mapping

```python
AGENT_GATEWAY_CONFIG = {
    "LogsAgent": ["observability-gateway"],
    "MetricsAgent": ["observability-gateway"],
    "TracesAgent": ["observability-gateway"],
    "ResourceAgent": ["resources-gateway"],
    "NotificationAgent": ["notification-gateway"],
    # Agents can use multiple gateways if needed
    "HybridAgent": ["observability-gateway", "resources-gateway"]
}
```

### Design Principles

- **Pre-configured Tool Access**: Static agent-to-gateway mapping for simplicity
- **IAM Authentication**: All gateways use AWS SigV4 for authentication
- **One Agent Per Task**: Executor creates fresh agent instances with task-specific prompts
- **Single Row Context**: One DynamoDB row per investigation with task-prefixed findings
- **Feedback Loop**: Executor triggers Brain re-evaluation after each task
- **Adaptive Workflows**: Brain adjusts investigation based on accumulated findings
- **1:N Gateway Mapping**: Each agent can access multiple gateways (typically 1)

### Data Stores

**Investigation Workflow Table** (`aiops-investigations`)
- Stores workflow metadata, tasks, and execution plan
- Partition Key: `investigation_id`, Sort Key: `item_type`
- Item types: METADATA, TASK#{task_id}, RESULT#{task_id}

**Investigation Context Table** (`aiops-investigation-context`)
- Single row per investigation tracking progress
- Partition Key: `investigation_id`
- Contains: alarm_summary, status, confidence, hypothesis, findings, timeline
- Findings keyed by `{task_id}_{agent_type}` to prevent duplication

## Current Status

✅ **Completed:**

- Core data models and enums
- Base agent communication infrastructure
- Brain Agent with alarm processing and workflow generation
- Brain Agent re-evaluation based on findings
- Executor Agent with task execution
- Investigation context store (single-row design)
- Context update after each task
- Feedback loop (Executor → Brain via SQS)
- Message routing (ALARM, EXECUTION, RE_EVALUATE)
- DynamoDB tables (workflow + context)
- MCP gateway integration
- Tool loading infrastructure

🚧 **In Progress:**

- Testing end-to-end workflow
- Additional specialized agents (MetricsAgent, TracesAgent, ResourceAgent)

📋 **Planned:**

- Confidence-based workflow adaptation
- Analysis report generation
- Notification integration
- Monitoring and observability

## Project Structure

``` text
aiops/
├── agents/          # Agent implementations
│   ├── base.py      # Base agent class and communication
│   ├── brain_agent.py  # Brain Agent implementation
│   ├── executor_agent.py  # Executor Agent with Strands Graph
│   ├── logs_agent.py      # CloudWatch Logs specialist
│   ├── metrics_agent.py   # CloudWatch Metrics specialist
│   ├── traces_agent.py    # X-Ray traces specialist
│   ├── resource_agent.py  # AWS resources specialist
│   ├── notification_agent.py  # Notification specialist
│   └── interfaces.py   # Agent interface definitions
├── models/          # Data models and enums
│   ├── data_models.py  # Core data structures
│   └── enums.py        # System enumerations
├── tools/           # Tool integration layer
│   ├── mcp_client.py      # MCP client with SigV4 auth
│   ├── gateway_config.py  # Agent-to-gateway mapping
│   └── tool_loader.py     # Tool discovery and loading
└── utils/           # Utility modules
    ├── logging.py   # Logging configuration
    └── validation.py # Validation utilities

tests/               # Test suite
├── gateway/         # Gateway integration tests
│   ├── test_notification_gateway_function.py
│   └── streamable_http_sigv4.py
├── test_brain_agent.py    # Automated Brain Agent tests
├── brain_agent_cli.py     # Interactive CLI for testing
└── README.md             # Test documentation

cdk/                 # Infrastructure as Code
├── lib/
│   ├── aiops-stack.ts     # Main stack with gateways
│   └── ecr-stack.ts       # ECR repository
└── lambda/          # Lambda functions for gateways
    └── feishu_notifier.py

.kiro/specs/aiops-root-cause-analysis/  # Specification documents
├── requirements.md  # System requirements
├── design.md       # Architecture and design
└── tasks.md        # Implementation tasks
```

## Testing

### Quick Start

Run all automated tests:

```bash
python run_tests.py
```

### Individual Test Options

**Automated Test Suite:**

```bash
python tests/test_brain_agent.py
```

**Interactive CLI Testing:**

```bash
python tests/brain_agent_cli.py
```

### Test Coverage

The current test suite covers:

- ✅ Alarm processing and validation
- ✅ Workflow generation for different alarm types (CPU, Memory, Database, Disk, Network)
- ✅ Confidence assessment algorithms
- ✅ Analysis report generation
- ✅ Root cause candidate identification
- ✅ Recommendation generation

## Features

### Brain Agent Capabilities

- **Alarm Categorization**: Automatically categorizes AWS CloudWatch alarms
- **Workflow Generation**: Creates investigation workflows with specific steps
- **Confidence Assessment**: Evaluates investigation confidence based on findings
- **Analysis Reports**: Generates comprehensive reports with root cause candidates
- **Adaptive Workflows**: Updates workflows based on execution feedback

### Supported Alarm Types

1. **CPU Utilization** (AWS/EC2)
2. **Memory Utilization** (AWS/EC2)
3. **Database Connections** (AWS/RDS)
4. **Disk Space** (AWS/EC2)
5. **Network Latency** (AWS/ApplicationELB)

## Development

### Requirements

- Python 3.8+
- Dependencies defined in the project modules

### Environment Variables

The following environment variables must be set (exported from CDK outputs):

```bash
export OBSERVABILITY_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
export RESOURCES_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
export NOTIFICATION_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
export INVESTIGATION_QUEUE_URL="https://sqs.REGION.amazonaws.com/ACCOUNT/aiops-investigations"
export INVESTIGATIONS_TABLE="aiops-investigations"
export CONTEXT_TABLE="aiops-investigation-context"
export AWS_REGION="ap-southeast-1"
```

These URLs are output by the CDK stack deployment.

### Deployment to AgentCore Runtime

```bash
# Optional: Set custom stack name prefix (default: aiops-demo)
export STACK_NAME_PREFIX=aiops-demo

# 1. Deploy ECR stack first
cd cdk && cdk deploy ${STACK_NAME_PREFIX}-ecr

# 2. Build and push Docker image
cd ../aiops
export AWS_REGION=ap-southeast-1
export AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export REPO_NAME=${STACK_NAME_PREFIX}-ecr-aiops-agent

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

docker build --platform linux/arm64 -t $REPO_NAME .
docker tag ${REPO_NAME}:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest

# 3. Deploy main stack with image URI
cd ../cdk
cdk deploy ${STACK_NAME_PREFIX}-main --parameters ImageUri=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/${REPO_NAME}:latest

# 4. Test the deployed agent
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn <ARN_FROM_CDK_OUTPUT> \
  --qualifier DEFAULT \
  --payload $(echo '{"prompt": "Analyze high CPU alarm"}' | base64) \
  response.json
```

### Running Tests

From the project root:

```bash
# Run all tests
python run_tests.py

# Run specific test
python tests/test_brain_agent.py

# Interactive testing
python tests/brain_agent_cli.py
```

### Next Steps

1. Complete Brain Agent workflow adaptation (Task 2.2)
2. Implement Executor Agent for workflow execution
3. Implement Evaluator Agent for completion assessment
4. Add multi-agent orchestration with Strands Graph
5. Create system entry point and CLI interface

## Contributing

This project follows a spec-driven development approach. See `.kiro/specs/aiops-root-cause-analysis/` for detailed requirements, design, and implementation tasks.

## License

[Add license information here]