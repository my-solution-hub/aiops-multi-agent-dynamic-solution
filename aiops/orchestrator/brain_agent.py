"""Brain Agent for alarm analysis and workflow generation."""

from strands import Agent
from strands.models import BedrockModel
from aiops.tools.gateway_config import AGENT_GATEWAY_CONFIG, get_agent_description
from aiops.tools.storage_tools import save_investigation_workflow, trigger_investigation
from aiops.utils.context_store import InvestigationContextStore
from aiops.utils.online_logger import log
from typing import Dict
import json
import uuid
import boto3
import os

class BrainAgent:
    """Brain Agent processes alarms and generates investigation workflows."""
    
    def __init__(self):
        self.model = BedrockModel(model_id="apac.anthropic.claude-sonnet-4-20250514-v1:0")
        self.context_store = InvestigationContextStore()
        self.sqs = boto3.client('sqs')
        self.agent = Agent(
            model=self.model,
            tools=[save_investigation_workflow, trigger_investigation],
            system_prompt=self._get_system_prompt()
        )
        self.evaluator_agent = Agent(
            model=self.model,
            tools=[save_investigation_workflow, trigger_investigation],
            system_prompt=self._get_evaluator_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        # Dynamically build available agents list with descriptions
        agents_info = []
        for agent_name in AGENT_GATEWAY_CONFIG.keys():
            description = get_agent_description(agent_name)
            agents_info.append(f"- {agent_name}: {description}")
        
        agents_list = "\n".join(agents_info)
        
        return f"""You are the Brain Agent for AIOps root cause analysis.

Your responsibilities:
1. Extract alarm information from input text
2. Categorize the alarm type and identify affected resources
3. Generate investigation tasks for specialized agents
4. Save the workflow using save_investigation_workflow tool
5. Trigger execution using trigger_investigation tool

Available specialized agents:
{agents_list}

When processing alarm text:
- Extract: alarm name, metric, namespace, threshold, dimensions, state
- Identify affected resources (the ones you can get the ARN or ID of the resources)
- Determine alarm severity and impact

IMPORTANT: 
1. After generating and saving workflow, call trigger_investigation to start execution.
2. If you decide to notify the on-call team, put the task after the investigation tasks.
3. include alarm key information in the notification task description.

Response format for workflow:
{{
  "alarm_summary": {{
    "resource_name": "string - alarm name",
    "metric": "string - metric name",
    "namespace": "string - AWS namespace",
    "resource_id": "string - affected resource ID",
    "time": "string - converts to an integer (removes milliseconds/decimal places)"
  }},
  "tasks": [
    {{
      "task_id": "string - unique task ID (e.g., task-1)",
      "agent_type": "string - one of the available agents",
      "description": "string - specific investigation task with detail information provided in description",
      "priority": number - priority level (1=highest)
    }}
  ]
}}

Select appropriate agents based on alarm type and generate actionable investigation tasks."""
    
    def _get_evaluator_prompt(self) -> str:
        """Get system prompt for re-evaluation."""
        agents_info = []
        for agent_name in AGENT_GATEWAY_CONFIG.keys():
            description = get_agent_description(agent_name)
            agents_info.append(f"- {agent_name}: {description}")
        
        agents_list = "\n".join(agents_info)
        
        return f"""You are the Brain Agent evaluating investigation progress.

Your responsibilities:
1. Analyze accumulated findings from completed tasks
2. Assess confidence level (0.0-1.0) based on evidence
3. Determine if investigation should continue or conclude
4. Generate additional tasks if needed

Available specialized agents:
{agents_list}

Evaluation criteria:
- Confidence >= 0.8: Investigation can conclude
- Confidence < 0.8: Continue investigation or add tasks
- Consider: evidence quality, consistency, completeness

If continuing investigation:
- Use save_investigation_workflow to add new tasks
- Use trigger_investigation to resume execution

If concluding:
- Do NOT call any tools
- Provide summary of findings and root cause"""
    
    def process_alarm_text(self, alarm_text: str, investigation_id: str = None) -> str:
        """Process alarm text and generate investigation workflow.
        
        Args:
            alarm_text: Raw alarm text (JSON or plain text)
            investigation_id: Investigation ID (generates UUID if not provided)
            
        Returns:
            Investigation ID
        """
        if investigation_id is None:
            investigation_id = str(uuid.uuid4())
        
        log("brain-init", f"Processing alarm for investigation {investigation_id}", investigation_id=investigation_id)
        
        prompt = f"""Analyze this CloudWatch alarm and generate investigation workflow.

Investigation ID: {investigation_id}
Alarm:
{alarm_text}

Generate tasks and save the workflow using save_investigation_workflow tool."""
        
        response = self.agent(prompt)
        
        # Initialize context (alarm_summary will be extracted from workflow)
        try:
            from aiops.utils.dynamodb_helper import InvestigationStore
            store = InvestigationStore()
            workflow = store.get_workflow(investigation_id)
            alarm_summary = workflow.get('alarm_summary', {})

            if alarm_summary:
                self.context_store.create_context(investigation_id, alarm_summary)
                log("brain-init", f"Context initialized with {len(workflow.get('tasks', []))} tasks", investigation_id=investigation_id)
                print(f"✅ Context initialized for {investigation_id}")
        except Exception as e:
            log("brain-init", f"Failed to initialize context: {e}", level="ERROR", investigation_id=investigation_id)
            print(f"⚠️  Failed to initialize context: {e}")
        return investigation_id
    
    def re_evaluate_workflow(self, investigation_id: str) -> str:
        """Re-evaluate workflow based on current context and findings.

        Args:
            investigation_id: Investigation ID
            
        Returns:
            Status message
        """
        log("brain-evaluate", f"Re-evaluating investigation {investigation_id}", investigation_id=investigation_id)
        
        # Get current context
        context = self.context_store.get_context(investigation_id)
        if not context:
            log("brain-evaluate", f"No context found for {investigation_id}", level="ERROR", investigation_id=investigation_id)
            return f"Error: No context found for {investigation_id}"
        
        # Get current workflow
        from aiops.utils.dynamodb_helper import InvestigationStore
        store = InvestigationStore()
        workflow = store.get_workflow(investigation_id)
        
        completed = len([t for t in workflow.get('tasks', []) if t.get('status') == 'COMPLETED'])
        pending = len([t for t in workflow.get('tasks', []) if t.get('status') == 'PENDING'])
        log("brain-evaluate", f"Completed: {completed}, Pending: {pending}, Confidence: {context.get('confidence', 0)}", investigation_id=investigation_id)

        prompt = f"""Re-evaluate investigation workflow based on findings.

Investigation ID: {investigation_id}

Current Context:
- Status: {context.get('status')}
- Confidence: {context.get('confidence')}
- Hypothesis: {context.get('current_hypothesis')}
- Findings: {json.dumps(context.get('findings', {}), indent=2)}
- Timeline: {json.dumps(context.get('timeline', []), indent=2)}

Current Workflow:
- Completed Tasks: {completed}
- Pending Tasks: {pending}

Evaluate the findings and decide next steps."""
        
        response = self.evaluator_agent(prompt)
        log("brain-evaluate", "Evaluation complete", investigation_id=investigation_id)
        
        # Send SQS message to continue execution
        queue_url = os.getenv('INVESTIGATION_QUEUE_URL')
        if queue_url:
            self.sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'message_type': 'EXECUTION',
                    'investigation_id': investigation_id
                })
            )
            print(f"✅ Re-evaluation complete, execution triggered")
        
        return f"Re-evaluation complete for {investigation_id}"
