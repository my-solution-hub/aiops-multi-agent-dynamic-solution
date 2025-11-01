"""Logs Agent for collecting and analyzing CloudWatch logs"""

import json
from typing import Dict, List, Any
from .base_tool_agent import BaseToolAgent
from ..orchestrator.base import tool, SystemState


class LogsAgent(BaseToolAgent):
    """Agent specialized in collecting and analyzing AWS CloudWatch logs"""
    
    def __init__(self, system_state: SystemState):
        super().__init__(
            agent_id="logs_agent",
            system_state=system_state
        )
        self.capabilities = [
            "cloudwatch_logs_collection",
            "log_pattern_analysis",
            "error_detection",
            "log_correlation",
            "log_filtering"
        ]
    
    def get_specialty(self) -> str:
        return "AWS CloudWatch logs collection and analysis"
    
    def _get_responsibilities(self) -> str:
        return """- Collect CloudWatch logs from specified log groups
- Analyze log patterns and identify errors
- Correlate log events across different sources
- Filter and search logs based on criteria
- Extract insights from application and system logs"""
    
    def get_available_operations(self) -> List[str]:
        return [
            "collect_logs",
            "analyze_patterns",
            "detect_errors",
            "correlate_events",
            "generate_log_report"
        ]
    
    def get_tools(self) -> List:
        """Get the tools available to the Logs Agent"""
        return [
            self._collect_logs_tool(),
            self._analyze_patterns_tool(),
            self._detect_errors_tool(),
            self._correlate_events_tool(),
            self._generate_report_tool()
        ]
    
    def _collect_logs_tool(self):
        """Tool for collecting CloudWatch logs"""
        @tool
        def collect_logs(log_request: str) -> str:
            """Collect CloudWatch logs from specified log groups.
            
            Args:
                log_request: JSON string with log collection parameters
                
            Returns:
                JSON string with collected log data
            """
            try:
                request = json.loads(log_request)
                result = self.execute_task("collect_logs", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to collect logs: {str(e)}"})
        
        return collect_logs
    
    def _analyze_patterns_tool(self):
        """Tool for analyzing log patterns"""
        @tool
        def analyze_log_patterns(pattern_request: str) -> str:
            """Analyze patterns in log data to identify trends and issues.
            
            Args:
                pattern_request: JSON string with pattern analysis parameters
                
            Returns:
                JSON string with pattern analysis results
            """
            try:
                request = json.loads(pattern_request)
                result = self.execute_task("analyze_patterns", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to analyze patterns: {str(e)}"})
        
        return analyze_log_patterns
    
    def _detect_errors_tool(self):
        """Tool for detecting errors in logs"""
        @tool
        def detect_log_errors(error_request: str) -> str:
            """Detect errors and exceptions in log data.
            
            Args:
                error_request: JSON string with error detection parameters
                
            Returns:
                JSON string with error detection results
            """
            try:
                request = json.loads(error_request)
                result = self.execute_task("detect_errors", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to detect errors: {str(e)}"})
        
        return detect_log_errors
    
    def _correlate_events_tool(self):
        """Tool for correlating log events"""
        @tool
        def correlate_log_events(correlation_request: str) -> str:
            """Correlate log events across different sources and time periods.
            
            Args:
                correlation_request: JSON string with correlation parameters
                
            Returns:
                JSON string with correlation results
            """
            try:
                request = json.loads(correlation_request)
                result = self.execute_task("correlate_events", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to correlate events: {str(e)}"})
        
        return correlate_log_events
    
    def _generate_report_tool(self):
        """Tool for generating log analysis reports"""
        @tool
        def generate_log_report(report_request: str) -> str:
            """Generate comprehensive log analysis report.
            
            Args:
                report_request: JSON string with report generation parameters
                
            Returns:
                JSON string with generated report
            """
            try:
                request = json.loads(report_request)
                result = self.execute_task("generate_log_report", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to generate report: {str(e)}"})
        
        return generate_log_report
    
    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a logs-related task"""
        if task_description == "collect_logs":
            return self._collect_log_data(context)
        elif task_description == "analyze_patterns":
            return self._analyze_log_patterns(context)
        elif task_description == "detect_errors":
            return self._detect_log_errors(context)
        elif task_description == "correlate_events":
            return self._correlate_log_events(context)
        elif task_description == "generate_log_report":
            return self._generate_logs_report(context)
        else:
            return {"error": f"Unknown task: {task_description}"}
    
    def _collect_log_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect CloudWatch logs data"""
        # Mock implementation - in real system would use boto3 CloudWatch Logs client
        return {
            "status": "success",
            "logs_collected": [
                {
                    "log_group": context.get("log_group", "/aws/lambda/my-function"),
                    "log_stream": "2024/01/01/[$LATEST]abcd1234",
                    "events": [
                        {
                            "timestamp": "2024-01-01T12:00:00Z",
                            "message": "INFO: Processing request",
                            "level": "INFO"
                        },
                        {
                            "timestamp": "2024-01-01T12:00:05Z", 
                            "message": "ERROR: Database connection failed",
                            "level": "ERROR"
                        }
                    ]
                }
            ],
            "collection_time": "2024-01-01T12:15:00Z",
            "total_events": 2
        }
    
    def _analyze_log_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in log data"""
        return {
            "status": "success",
            "pattern_analysis": {
                "common_patterns": [
                    {"pattern": "Database connection failed", "frequency": 15, "severity": "high"},
                    {"pattern": "Processing request", "frequency": 100, "severity": "low"}
                ],
                "temporal_patterns": {
                    "peak_error_time": "12:00-12:05 UTC",
                    "error_frequency": "every 30 seconds"
                }
            }
        }
    
    def _detect_log_errors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect errors in log data"""
        return {
            "status": "success",
            "error_detection": {
                "errors_found": 3,
                "error_types": [
                    {
                        "type": "DatabaseConnectionError",
                        "count": 2,
                        "first_occurrence": "2024-01-01T12:00:05Z",
                        "last_occurrence": "2024-01-01T12:00:35Z"
                    }
                ],
                "error_rate": 0.03,
                "severity_distribution": {"high": 2, "medium": 1, "low": 0}
            }
        }
    
    def _correlate_log_events(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate log events across sources"""
        return {
            "status": "success",
            "correlation_analysis": {
                "correlated_events": [
                    {
                        "correlation_id": "corr_001",
                        "events": [
                            {"source": "application", "timestamp": "2024-01-01T12:00:00Z", "message": "Request started"},
                            {"source": "database", "timestamp": "2024-01-01T12:00:05Z", "message": "Connection timeout"}
                        ],
                        "correlation_strength": 0.95
                    }
                ],
                "timeline": "5 second delay between request and database error"
            }
        }
    
    def _generate_logs_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive logs report"""
        return {
            "status": "success",
            "report": {
                "summary": "Log analysis completed for specified time period",
                "key_findings": [
                    "Database connection errors detected",
                    "Error rate increased during peak hours",
                    "Strong correlation between request volume and errors"
                ],
                "recommendations": [
                    "Investigate database connection pool settings",
                    "Implement connection retry logic",
                    "Monitor database performance metrics"
                ],
                "error_summary": {
                    "total_errors": 3,
                    "unique_error_types": 1,
                    "most_frequent_error": "DatabaseConnectionError"
                }
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities