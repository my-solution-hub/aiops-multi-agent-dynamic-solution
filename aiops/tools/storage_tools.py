"""Storage tools for agents to save investigation data."""

import boto3
import json
import os
from datetime import datetime
from strands.tools import tool
from aiops.utils.dynamodb_helper import InvestigationStore
from aiops.utils.context_store import InvestigationContextStore
from aiops.models.enums import MessageType
from typing import Dict, List

store = InvestigationStore()
context_store = InvestigationContextStore()
sqs = boto3.client('sqs')

@tool
def update_confidence(
    investigation_id: str,
    confidence: float,
    hypothesis: str,
    root_cause_candidates: List[str]
) -> str:
    """Update investigation confidence and hypothesis.
    
    Args:
        investigation_id: Investigation ID
        confidence: Confidence score (0.0-1.0)
        hypothesis: Current hypothesis about root cause
        root_cause_candidates: List of potential root causes
        
    Returns:
        Success message
    """
    context_store.update_hypothesis(investigation_id, hypothesis, confidence, root_cause_candidates)
    return f"Updated confidence to {confidence:.2f}"

@tool
def save_investigation_workflow(
    investigation_id: str,
    alarm_summary: Dict,
    tasks: List[Dict]
) -> str:
    """Save investigation workflow to DynamoDB.
    
    Args:
        investigation_id: Unique investigation ID
        alarm_summary: Alarm summary with resource_name, metric, namespace, resource_id, time
        tasks: List of tasks with task_id, agent_type, description, priority
        
    Returns:
        Success message
    """
    # Ensure required fields exist with defaults
    alarm_summary.setdefault('resource_name', 'unknown')
    alarm_summary.setdefault('metric', 'unknown')
    alarm_summary.setdefault('namespace', 'unknown')
    alarm_summary.setdefault('resource_id', 'unknown')
    alarm_summary.setdefault('time', str(int(datetime.utcnow().timestamp())))
    
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
def store_task_findings(
    investigation_id: str,
    task_id: str,
    summary: str,
    key_findings: List[str],
    evidence: List[str] = None,
    recommendations: List[str] = None
) -> str:
    """Store structured findings from task execution.
    
    Args:
        investigation_id: Investigation ID
        task_id: Task ID
        summary: Brief summary of findings
        key_findings: List of key findings or observations
        evidence: Optional list of supporting evidence
        recommendations: Optional list of recommendations
        
    Returns:
        Success message
    """
    finding_data = {
        "summary": summary,
        "key_findings": key_findings,
        "evidence": evidence or [],
        "recommendations": recommendations or [],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Get agent type from task
    workflow = store.get_workflow(investigation_id)
    task = next((t for t in workflow.get('tasks', []) if t.get('task_id') == task_id), None)
    agent_type = task.get('agent_type', 'Unknown') if task else 'Unknown'
    
    context_store.update_finding(investigation_id, task_id, agent_type, finding_data)
    return f"Findings stored for task {task_id}"

@tool
def get_investigation_summary(investigation_id: str) -> Dict:
    """Get investigation summary including hypothesis, findings, and confidence.
    
    Args:
        investigation_id: Investigation ID
        
    Returns:
        Dict with investigation summary
    """
    context = context_store.get_context(investigation_id)
    if not context:
        return {"error": f"No context found for investigation {investigation_id}"}
    
    workflow = store.get_workflow(investigation_id)
    
    return {
        "alarm_summary": workflow.get('alarm_summary', {}),
        "current_hypothesis": context.get('current_hypothesis', ''),
        "confidence": context.get('confidence', 0.0),
        "root_cause_candidates": context.get('root_cause_candidates', []),
        "findings": context.get('findings', {}),
        "status": context.get('status', 'UNKNOWN')
    }

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
