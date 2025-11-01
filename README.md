# AIOps Root Cause Analysis System

A multi-agent system for automated root cause analysis of AWS CloudWatch alarms using intelligent workflow generation and iterative investigation rounds.

## Architecture

The system employs three specialized agents working in a feedback loop:

- **Brain Agent**: Processes alarms, generates investigation workflows, and assesses confidence
- **Domain Analysis AI Agent**: AI Agent with tools and prompts to identify most relevant AWS resources
- **Executor Agent**: Orchestrates workflow execution across specialized agents *(coming soon)*
- **Evaluator Agent**: Assesses investigation completeness and quality *(coming soon)*

## Current Status

✅ **Completed:**

- Core data models and enums
- Base agent communication infrastructure
- Brain Agent with alarm processing and workflow generation
- Domain Analysis AI Agent with 6 AWS tools and 4 analysis prompts

🚧 **In Progress:**

- Task 2.2: Workflow generation and adaptation
- Task 2.3: Analysis report generation

📋 **Planned:**

- Executor Agent implementation
- Evaluator Agent implementation
- Multi-agent orchestration with Strands Graph

## Project Structure

``` text
aiops/
├── agents/          # Agent implementations
│   ├── base.py      # Base agent class and communication
│   ├── brain_agent.py  # Brain Agent implementation
│   ├── domain_analysis_agent.py  # Domain Analysis Agent
│   └── interfaces.py   # Agent interface definitions
├── models/          # Data models and enums
│   ├── data_models.py  # Core data structures
│   └── enums.py        # System enumerations
└── utils/           # Utility modules
    ├── logging.py   # Logging configuration
    └── validation.py # Validation utilities

tests/               # Test suite
├── test_brain_agent.py    # Automated Brain Agent tests
├── brain_agent_cli.py     # Interactive CLI for testing
└── README.md             # Test documentation

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