"""AIOps AgentCore Runtime Entry Point"""
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
import json

app = BedrockAgentCoreApp()

agent = Agent(
    name="AIOps Root Cause Analyzer",
    instructions="""You are an AWS CloudWatch alarm analyzer. 
    Analyze alarm data and provide root cause analysis with recommendations.
    Use available MCP tools to investigate AWS resources."""
)

@app.entrypoint
def invoke(payload):
    """Handle alarm investigation requests"""
    alarm = payload.get("alarm", {})
    prompt = payload.get("prompt", f"Analyze this CloudWatch alarm: {json.dumps(alarm)}")
    
    result = agent(prompt)
    
    return {
        "investigation_id": payload.get("investigation_id", "demo-001"),
        "analysis": result.message,
        "status": "completed"
    }

if __name__ == "__main__":
    app.run()
