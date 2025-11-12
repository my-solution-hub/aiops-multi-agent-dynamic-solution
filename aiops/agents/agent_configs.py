"""Agent configurations with prompts, formats, and context processing."""

from typing import Dict, Callable, Any
from datetime import datetime


class AgentConfig:
    """Configuration for a specialized agent."""
    
    def __init__(
        self,
        agent_type: str,
        system_prompt: str,
        output_format: Dict[str, Any],
        process_result: Callable[[Dict], Dict]
    ):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.output_format = output_format
        self.process_result = process_result


def process_logs_result(result: Dict) -> Dict:
    """Process LogsAgent result for context storage."""
    return {
        "error_count": result.get("error_count", 0),
        "errors": result.get("errors", []),
        "info": result.get("info", []),
        "key_patterns": result.get("patterns", []),
        "log_summary": result.get("summary", ""),
        "time_range": result.get("time_range", "")
    }


def process_metrics_result(result: Dict) -> Dict:
    """Process MetricsAgent result for context storage."""
    return {
        "peak_value": result.get("peak", 0),
        "average_value": result.get("average", 0),
        "trend": result.get("trend", ""),
        "anomalies": result.get("anomalies", [])
    }


def process_root_cause_result(result: Dict) -> Dict:
    """Process RootCauseAnalysisAgent result for context storage."""
    return {
        "root_cause_statement": result.get("root_cause", ""),
        "top_findings": result.get("findings", []),
        "confidence_assessment": result.get("confidence", ""),
        "summary": result.get("summary", "")
    }


def process_notification_result(result: Dict) -> Dict:
    """Process NotificationAgent result for context storage."""
    return {
        "notification_sent": result.get("sent", False),
        "recipients": result.get("recipients", []),
        "message": result.get("message", "")
    }


# Agent configurations
AGENT_CONFIGS = {
    "LogsAgent": AgentConfig(
        agent_type="LogsAgent",
        system_prompt="""You are a CloudWatch Logs analysis expert.

Your responsibilities:
- Query CloudWatch Logs for errors, warnings, and patterns
- Identify errors in log messages
- Correlate log events with alarm timeline
- Summarize findings concisely

IMPORTANT: Use store_task_findings tool to save your analysis with:
- summary: Brief overview of what you found in logs
- key_findings: List of important observations (error patterns, anomalies, trends)
- evidence: List of specific log entries or error messages
- recommendations: List of next steps or areas to investigate

Use the provided tools to query logs. Focus on the time period around the alarm.""",
        output_format={
            "error_count": "number",
            "errors": ["string"],
            "info": ["string"],
            "patterns": ["string"],
            "summary": "string",
            "time_range": "string"
        },
        process_result=process_logs_result
    ),
    
    "MetricsAgent": AgentConfig(
        agent_type="MetricsAgent",
        system_prompt="""You are a CloudWatch Metrics analysis expert.

Your responsibilities:
- Query CloudWatch Metrics for performance data
- Identify metric trends and anomalies
- Correlate metrics with alarm threshold
- Determine if issue is ongoing or resolved

Output format:
{
  "peak": <number>,
  "average": <number>,
  "trend": "<increasing|decreasing|stable>",
  "anomalies": [<list of anomalies>]
}

Use the provided tools to query metrics. Analyze the time period around the alarm.""",
        output_format={
            "peak": "number",
            "average": "number",
            "trend": "string",
            "anomalies": ["string"]
        },
        process_result=process_metrics_result
    ),
    
    "NotificationAgent": AgentConfig(
        agent_type="NotificationAgent",
        system_prompt="""You are a notification delivery expert.

Your responsibilities:
- Get investigation summary using get_investigation_summary tool
- Format investigation summary clearly for on-call team
- Include alarm details, hypothesis, confidence, and key findings
- Send notification using available notification tools

IMPORTANT: 
1. FIRST call get_investigation_summary to get investigation details
2. Format a clear message with: alarm info, root cause hypothesis, confidence level, key findings
3. Send notification with the formatted message

Use the provided tools to get investigation data and send notifications.""",
        output_format={
            "sent": "boolean",
            "recipients": ["string"],
            "message": "string"
        },
        process_result=process_notification_result
    ),
    
    "RootCauseAnalysisAgent": AgentConfig(
        agent_type="RootCauseAnalysisAgent",
        system_prompt="""You are a root cause analysis expert.

Your responsibilities:
- Analyze all accumulated findings from investigation
- Determine the most likely root cause
- Provide confidence assessment in string format
- Summarize key evidence supporting the conclusion

Output format:
{
  "root_cause": "<definitive root cause statement>",
  "findings": [<list of top 3-5 most relevant findings>],
  "confidence": "<High|Medium|Low with explanation>",
  "summary": "<brief investigation summary>"
}

Base your analysis on evidence from logs, metrics, and resource data. Be definitive in your conclusion.""",
        output_format={
            "root_cause": "string",
            "findings": ["string"],
            "confidence": "string",
            "summary": "string"
        },
        process_result=process_root_cause_result
    )
}


def get_agent_config(agent_type: str) -> AgentConfig:
    """Get configuration for an agent type."""
    return AGENT_CONFIGS.get(agent_type)


def get_system_prompt(agent_type: str, investigation_id: str) -> str:
    """Get system prompt for an agent with current time."""
    config = get_agent_config(agent_type)
    if not config:
        return f"You are {agent_type}. Use available tools to complete the task."
    
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    return f"Current time is {current_time}.\n\nInvestigation ID: {investigation_id}\n\n{config.system_prompt}"


def process_agent_result(agent_type: str, result: Dict) -> Dict:
    """Process agent result for context storage."""
    config = get_agent_config(agent_type)
    if not config or not config.process_result:
        return result
    
    try:
        return config.process_result(result)
    except Exception as e:
        print(f"⚠️  Error processing result for {agent_type}: {e}")
        return result
