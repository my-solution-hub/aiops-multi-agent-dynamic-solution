"""Storage tools for agents to save investigation data."""

import boto3
import json
import os
from strands.tools import tool
from aiops.utils.dynamodb_helper import InvestigationStore
from aiops.utils.context_store import InvestigationContextStore
from aiops.models.enums import MessageType
from typing import Dict, List

store = InvestigationStore()
context_store = InvestigationContextStore()
sqs = boto3.client('sqs')

@tool
def save_investigation_workflow(
    investigation_id: str,
    alarm_summary: Dict,
    tasks: List[Dict]
) -> str:
    """Save investigation workflow to DynamoDB.
    
    Args:
        investigation_id: Unique investigation ID
        alarm_summary: Alarm summary with name, metric, namespace, resource_id
        tasks: List of tasks with task_id, agent_type, description, priority
        
    Returns:
        Success message
    """
    store.save_workflow(investigation_id, alarm_summary, tasks)
    return f"Workflow saved for investigation {investigation_id} with {len(tasks)} tasks"

@tool
def trigger_investigation(investigation_id: str) -> str:
    """Trigger investigation execution by sending message to SQS queue.
    
    Args:
        investigation_id: Investigation ID to execute
        
    Returns:
        Success message
    """
    queue_url = os.getenv('INVESTIGATION_QUEUE_URL')
    if not queue_url:
        return "Error: INVESTIGATION_QUEUE_URL not configured"
    
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            'message_type': MessageType.EXECUTION.value,
            'investigation_id': investigation_id
        })
    )
    return f"Investigation {investigation_id} triggered for execution"

@tool
def get_alarm_summary(investigation_id: str) -> Dict:
    """Get alarm summary for an investigation from DynamoDB.
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        Alarm summary dict with alarm_name, metric_name, namespace, resource_id, threshold, etc.
    """
    workflow = store.get_workflow(investigation_id)
    alarm_summary = workflow.get('alarm_summary', {})
    
    if not alarm_summary:
        return {"error": f"No alarm summary found for investigation {investigation_id}"}
    
    return alarm_summary

@tool
def get_next_task(investigation_id: str) -> Dict:
    """Get the next task to execute from investigation workflow.
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        Task dict with task_id, agent_type, description, priority
    """
    task = store.get_next_task(investigation_id)
    if task:
        return {
            "task_id": task['task_id'],
            "agent_type": task['agent_type'],
            "description": task['description'],
            "priority": task['priority']
        }
    return {"message": "No pending tasks"}

@tool
def complete_task(
    investigation_id: str,
    task_id: str,
    result: Dict
) -> str:
    """Mark task as completed and save result.
    
    Args:
        investigation_id: Investigation ID
        task_id: Task ID
        result: Task execution result
        
    Returns:
        Success message
    """
    store.complete_task(investigation_id, task_id, result)
    return f"Task {task_id} completed for investigation {investigation_id}"

@tool
def update_context_finding(
    investigation_id: str,
    task_id: str,
    agent_type: str,
    finding_data: Dict
) -> str:
    """Update investigation context with task findings.
    
    Args:
        investigation_id: Investigation ID
        task_id: Task ID
        agent_type: Agent type
        finding_data: Finding data dict
        
    Returns:
        Success message
    """
    context_store.update_finding(investigation_id, task_id, agent_type, finding_data)
    return f"Context updated for {task_id}_{agent_type}"

@tool
def add_context_event(
    investigation_id: str,
    event: str,
    source: str
) -> str:
    """Add event to investigation timeline.
    
    Args:
        investigation_id: Investigation ID
        event: Event description
        source: Event source (agent name)
        
    Returns:
        Success message
    """
    context_store.add_timeline_event(investigation_id, event, source)
    return f"Event added to timeline: {event}"

@tool
def get_investigation_context(investigation_id: str) -> Dict:
    """Get full investigation context.
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        Full context dict
    """
    context = context_store.get_context(investigation_id)
    if not context:
        return {"error": f"No context found for investigation {investigation_id}"}
    return context
