"""Brain Agent for alarm analysis and workflow generation."""

from strands import Agent
from strands.models import BedrockModel
from aiops.tools.gateway_config import AGENT_GATEWAY_CONFIG, get_agent_description
from aiops.tools.storage_tools import save_investigation_workflow, trigger_investigation
from typing import Dict
import json
import uuid

class BrainAgent:
    """Brain Agent processes alarms and generates investigation workflows."""
    
    def __init__(self):
        self.model = BedrockModel(model_id="apac.amazon.nova-pro-v1:0")
        self.agent = Agent(
            model=self.model,
            tools=[save_investigation_workflow, trigger_investigation],
            system_prompt=self._get_system_prompt()
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
- Identify affected resources (instance IDs, database names, etc.)
- Determine alarm severity and impact

IMPORTANT: After generating and saving workflow, call trigger_investigation to start execution.

Response format for workflow:
{{
  "alarm_summary": {{
    "name": "string - alarm name",
    "metric": "string - metric name",
    "namespace": "string - AWS namespace",
    "resource_id": "string - affected resource ID"
  }},
  "tasks": [
    {{
      "task_id": "string - unique task ID (e.g., task-1)",
      "agent_type": "string - one of the available agents",
      "description": "string - specific investigation task",
      "priority": number - priority level (1=highest)
    }}
  ]
}}

Select appropriate agents based on alarm type and generate actionable investigation tasks."""
    
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
        
        prompt = f"""Analyze this CloudWatch alarm and generate investigation workflow.

Investigation ID: {investigation_id}
Alarm:
{alarm_text}

Generate tasks and save the workflow using save_investigation_workflow tool."""
        
        response = self.agent(prompt)
        return investigation_id
