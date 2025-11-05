# AIOps Architecture Design

## Overview

Task-driven multi-agent system with MCP gateway integration for AWS CloudWatch alarm root cause analysis.

## Flow

```
CloudWatch Alarm 
    ↓
Brain Agent (analyzes alarm, generates tasks)
    ↓
Executor Agent (creates specialized agents per task)
    ↓
Specialized Agents (use MCP tools from gateways)
    ↓
MCP Gateways (expose domain-specific tools)
    ↓
AWS Services (CloudWatch, EC2, RDS, etc.)
```

## Components

### 1. Brain Agent
- Processes CloudWatch alarms
- Generates investigation tasks with specific prompts
- Assesses confidence levels
- Creates analysis reports

### 2. Executor Agent
- Receives tasks from Brain Agent
- Creates new agent instance per task (with task-specific prompt)
- Uses Strands Graph for orchestration
- Aggregates results back to Brain Agent

### 3. Specialized Agents

| Agent | Purpose | Gateways |
|-------|---------|----------|
| LogsAgent | CloudWatch Logs analysis | observability-gateway |
| MetricsAgent | CloudWatch Metrics analysis | observability-gateway |
| TracesAgent | X-Ray traces analysis | observability-gateway |
| ResourceAgent | AWS resource inspection | resources-gateway |
| NotificationAgent | Alert delivery | notification-gateway |

### 4. MCP Gateways

**Observability Gateway**
- CloudWatch Logs query tools
- CloudWatch Metrics query tools
- X-Ray traces query tools

**AWS Resources Gateway**
- EC2 describe/inspect tools
- RDS describe/inspect tools
- ELB describe/inspect tools
- Resource tagging tools

**Notification Gateway**
- Feishu notification tool
- Email notification (future)
- Slack notification (future)

## Design Decisions

### 1. Tool Access: Pre-configured (Static Mapping)
**Why**: Simplicity over dynamic discovery
- Agent-to-gateway mapping defined in `gateway_config.py`
- No runtime discovery complexity
- Clear, predictable tool access

### 2. Authentication: IAM (SigV4)
**Why**: Simpler than Cognito JWT
- Uses existing AWS credentials
- No token management needed
- Tested and working

### 3. Agent-Gateway Mapping: 1:N
**Why**: Flexibility with typical simplicity
- Most agents use 1 gateway
- Some agents can use multiple gateways if needed
- Example: HybridAgent uses both observability + resources

### 4. Agent Lifecycle: One Agent Per Task
**Why**: Task-specific prompts
- Each task has unique prompt requirements
- Fresh agent instance per task
- No state pollution between tasks

### 5. Orchestration: Strands Graph
**Why**: Easier coding
- Built-in flow management
- Handles agent coordination
- Simplifies executor implementation

## Tool Loading Flow

```python
# 1. Agent requests tools
tools = load_tools_for_agent("LogsAgent")

# 2. Tool loader checks config
gateways = get_gateways_for_agent("LogsAgent")  # ["observability-gateway"]

# 3. For each gateway
gateway_url = get_gateway_url("observability-gateway")  # from env

# 4. Create MCP client with SigV4
mcp_client = create_gateway_mcp_client(gateway_url)

# 5. List tools from gateway
tools = mcp_client.list_tools_sync()

# 6. Return tools to agent
return tools
```

## Environment Configuration

Required environment variables (from CDK outputs):

```bash
OBSERVABILITY_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
RESOURCES_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
NOTIFICATION_GATEWAY_URL="https://xxx.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp"
AWS_REGION="ap-southeast-1"
```

## Implementation Status

✅ **Completed:**
- Architecture design
- Gateway configuration structure
- MCP client with SigV4 auth
- Tool loader implementation
- Environment variable setup

🚧 **Next Steps:**
1. Update specialized agents to use tool loader
2. Implement Executor Agent with Strands Graph
3. Create CDK stacks for additional gateways
4. Integrate Brain Agent with Executor
