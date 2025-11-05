"""Executor Agent for sequential task execution."""

import os
import boto3
from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from aiops.utils.dynamodb_helper import InvestigationStore
from aiops.tools import load_tools_for_agent

class ExecutorAgent:
    """Executor Agent executes investigation tasks sequentially."""
    
    def __init__(self):
        self.store = InvestigationStore()
        
        # Use smaller max_tokens to reduce streaming time
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
            # model_id="apac.amazon.nova-pro-v1:0",
            # config={"max_tokens": 512, "temperature": 0.3}
        )
    
    def execute_workflow(self, investigation_id: str) -> dict:
        """Execute workflow for an investigation.
        
        Args:
            investigation_id: Investigation ID
            
        Returns:
            Execution summary
        """
        print(f"🚀 Starting workflow execution: {investigation_id}")
        
        try:
            # Get next task from DynamoDB
            task = self.store.get_next_task(investigation_id)
            
            if not task:
                print("❌ No pending tasks found")
                return {"status": "no_tasks", "investigation_id": investigation_id}
            
            print(f"📋 Executing task: {task['task_id']}")
            print(f"   Agent: {task['agent_type']}")
            print(f"   Description: {task['description']}")
            
            # Execute task with tools
            result = self.execute_task(task)
            
            # Mark complete in DynamoDB
            self.store.complete_task(investigation_id, task['task_id'], result)
            print(f"✅ Task {task['task_id']} completed")
            
            return {
                "status": "completed",
                "investigation_id": investigation_id,
                "task_id": task['task_id'],
                "result": result
            }
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            return {
                "status": "error",
                "investigation_id": investigation_id,
                "error": str(e)
            }
    
    def execute_task(self, task: dict) -> dict:
        """Execute a single task using appropriate agent with tools.
        
        Args:
            task: Task dict with agent_type and description
            
        Returns:
            Task execution result
        """
        agent_type = task['agent_type']
        description = task['description']
        
        try:
            from aiops.tools.mcp_client import create_gateway_mcp_client
            from aiops.tools.gateway_config import get_gateways_for_agent, get_gateway_url
            
            # Get gateway for this agent
            gateway_names = get_gateways_for_agent(agent_type)
            if not gateway_names:
                return {"status": "error", "error": f"No gateway configured for {agent_type}"}
            
            gateway_name = gateway_names[0]
            gateway_url = get_gateway_url(gateway_name)
            
            print(f"🔧 Connecting to gateway: {gateway_name}")
            mcp_client = create_gateway_mcp_client(gateway_url)
            
            # Keep MCP client session open during execution
            with mcp_client:
                # Load tools within context
                tools = []
                pagination_token = None
                while True:
                    result = mcp_client.list_tools_sync(pagination_token=pagination_token)
                    tools.extend(result)
                    if result.pagination_token is None:
                        break
                    pagination_token = result.pagination_token
                
                print(f"✅ Loaded {len(tools)} tools")
                
                # Create and execute agent within context
                print(f"🤖 Creating agent...")
                agent = Agent(
                    model=self.model,
                    tools=tools,
                    system_prompt=f"You are {agent_type}. Use available tools directly. Be concise."
                )
                
                print(f"▶️  Executing agent...")
                response = agent(description)
                print(f"✅ Agent execution completed")
                
                return {
                    "status": "completed",
                    "message": response.message if hasattr(response, 'message') else str(response)
                }
                
        except Exception as e:
            import traceback
            print(f"❌ Error executing task: {e}")
            print(f"📍 Traceback: {traceback.format_exc()[-500:]}")
            return {
                "status": "error",
                "error": str(e)
            }
