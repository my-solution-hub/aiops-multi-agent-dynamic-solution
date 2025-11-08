"""AIOps AgentCore Runtime Entry Point"""

from bedrock_agentcore import BedrockAgentCoreApp
from .orchestrator.brain_agent import BrainAgent
from .orchestrator.executor_agent import ExecutorAgent
from .models.enums import MessageType

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Route messages to Brain or Executor based on message_type."""
    message_type = payload.get("message_type", MessageType.ALARM.value)
    
    if message_type == MessageType.EXECUTION.value:
        investigation_id = payload.get("investigation_id")
        executor = ExecutorAgent()
        result = executor.execute_workflow(investigation_id)
        return {
            "investigation_id": investigation_id,
            "status": "execution_ongoing",
            "result": result
        }
    elif message_type == "RE_EVALUATE":
        investigation_id = payload.get("investigation_id")
        brain = BrainAgent()
        result = brain.re_evaluate_workflow(investigation_id)
        return {
            "investigation_id": investigation_id,
            "status": "re_evaluation_complete",
            "result": result
        }
    else:
        alarm_text = payload.get("alarm", payload.get("prompt", ""))
        brain = BrainAgent()
        investigation_id = brain.process_alarm_text(alarm_text)
        return {
            "investigation_id": investigation_id,
            "status": "investigation_triggered",
            "message": "Workflow created and execution queued"
        }

if __name__ == "__main__":
    app.run()


