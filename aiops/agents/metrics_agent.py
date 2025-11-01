"""Metrics Agent for collecting and analyzing CloudWatch metrics"""

import json
from typing import Dict, List, Any
from .base_tool_agent import BaseToolAgent
from ..orchestrator.base import tool, SystemState


class MetricsAgent(BaseToolAgent):
    """Agent specialized in collecting and analyzing AWS CloudWatch metrics"""
    
    def __init__(self, system_state: SystemState):
        super().__init__(
            agent_id="metrics_agent",
            system_state=system_state
        )
        self.capabilities = [
            "cloudwatch_metrics_collection",
            "metric_analysis",
            "threshold_evaluation",
            "trend_analysis",
            "anomaly_detection"
        ]
    
    def get_specialty(self) -> str:
        return "AWS CloudWatch metrics collection and analysis"
    
    def _get_responsibilities(self) -> str:
        return """- Collect CloudWatch metrics for specified resources
- Analyze metric trends and patterns
- Evaluate threshold breaches and anomalies
- Provide statistical analysis of metric data
- Generate metric-based insights and recommendations"""
    
    def get_available_operations(self) -> List[str]:
        return [
            "collect_metrics",
            "analyze_metric_trends", 
            "evaluate_thresholds",
            "detect_anomalies",
            "generate_metric_report"
        ]
    
    def get_tools(self) -> List:
        """Get the tools available to the Metrics Agent"""
        return [
            self._collect_metrics_tool(),
            self._analyze_trends_tool(),
            self._evaluate_thresholds_tool(),
            self._detect_anomalies_tool(),
            self._generate_report_tool()
        ]
    
    def _collect_metrics_tool(self):
        """Tool for collecting CloudWatch metrics"""
        @tool
        def collect_metrics(metric_request: str) -> str:
            """Collect CloudWatch metrics for specified resources.
            
            Args:
                metric_request: JSON string with metric collection parameters
                
            Returns:
                JSON string with collected metrics data
            """
            try:
                request = json.loads(metric_request)
                result = self.execute_task("collect_metrics", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to collect metrics: {str(e)}"})
        
        return collect_metrics
    
    def _analyze_trends_tool(self):
        """Tool for analyzing metric trends"""
        @tool
        def analyze_metric_trends(analysis_request: str) -> str:
            """Analyze trends in metric data over time.
            
            Args:
                analysis_request: JSON string with trend analysis parameters
                
            Returns:
                JSON string with trend analysis results
            """
            try:
                request = json.loads(analysis_request)
                result = self.execute_task("analyze_trends", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to analyze trends: {str(e)}"})
        
        return analyze_metric_trends
    
    def _evaluate_thresholds_tool(self):
        """Tool for evaluating metric thresholds"""
        @tool
        def evaluate_thresholds(threshold_request: str) -> str:
            """Evaluate metric values against defined thresholds.
            
            Args:
                threshold_request: JSON string with threshold evaluation parameters
                
            Returns:
                JSON string with threshold evaluation results
            """
            try:
                request = json.loads(threshold_request)
                result = self.execute_task("evaluate_thresholds", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to evaluate thresholds: {str(e)}"})
        
        return evaluate_thresholds
    
    def _detect_anomalies_tool(self):
        """Tool for detecting metric anomalies"""
        @tool
        def detect_anomalies(anomaly_request: str) -> str:
            """Detect anomalies in metric data using statistical analysis.
            
            Args:
                anomaly_request: JSON string with anomaly detection parameters
                
            Returns:
                JSON string with anomaly detection results
            """
            try:
                request = json.loads(anomaly_request)
                result = self.execute_task("detect_anomalies", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to detect anomalies: {str(e)}"})
        
        return detect_anomalies
    
    def _generate_report_tool(self):
        """Tool for generating metric analysis reports"""
        @tool
        def generate_metric_report(report_request: str) -> str:
            """Generate comprehensive metric analysis report.
            
            Args:
                report_request: JSON string with report generation parameters
                
            Returns:
                JSON string with generated report
            """
            try:
                request = json.loads(report_request)
                result = self.execute_task("generate_report", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to generate report: {str(e)}"})
        
        return generate_metric_report
    
    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a metrics-related task"""
        if task_description == "collect_metrics":
            return self._collect_metrics_data(context)
        elif task_description == "analyze_trends":
            return self._analyze_metric_trends(context)
        elif task_description == "evaluate_thresholds":
            return self._evaluate_metric_thresholds(context)
        elif task_description == "detect_anomalies":
            return self._detect_metric_anomalies(context)
        elif task_description == "generate_report":
            return self._generate_metrics_report(context)
        else:
            return {"error": f"Unknown task: {task_description}"}
    
    def _collect_metrics_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect CloudWatch metrics data"""
        # Mock implementation - in real system would use boto3 CloudWatch client
        return {
            "status": "success",
            "metrics_collected": [
                {
                    "metric_name": context.get("metric_name", "CPUUtilization"),
                    "namespace": context.get("namespace", "AWS/EC2"),
                    "dimensions": context.get("dimensions", {}),
                    "datapoints": [
                        {"timestamp": "2024-01-01T12:00:00Z", "value": 45.2},
                        {"timestamp": "2024-01-01T12:05:00Z", "value": 52.1},
                        {"timestamp": "2024-01-01T12:10:00Z", "value": 48.7}
                    ]
                }
            ],
            "collection_time": "2024-01-01T12:15:00Z",
            "data_quality": "high"
        }
    
    def _analyze_metric_trends(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in metric data"""
        return {
            "status": "success",
            "trend_analysis": {
                "overall_trend": "increasing",
                "trend_strength": 0.75,
                "seasonal_patterns": ["daily_peak_at_noon"],
                "anomalous_periods": []
            },
            "confidence": 0.85
        }
    
    def _evaluate_metric_thresholds(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate metrics against thresholds"""
        return {
            "status": "success",
            "threshold_evaluation": {
                "breaches_detected": 2,
                "breach_periods": [
                    {"start": "2024-01-01T12:05:00Z", "end": "2024-01-01T12:10:00Z", "severity": "warning"}
                ],
                "threshold_value": context.get("threshold", 50.0),
                "current_value": 52.1
            }
        }
    
    def _detect_metric_anomalies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in metric data"""
        return {
            "status": "success",
            "anomaly_detection": {
                "anomalies_found": 1,
                "anomaly_score": 0.92,
                "anomalous_datapoints": [
                    {"timestamp": "2024-01-01T12:05:00Z", "value": 52.1, "expected_range": [40, 50]}
                ]
            }
        }
    
    def _generate_metrics_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive metrics report"""
        return {
            "status": "success",
            "report": {
                "summary": "Metric analysis completed for specified time period",
                "key_findings": [
                    "CPU utilization trending upward",
                    "Threshold breach detected at 12:05 UTC",
                    "No significant anomalies beyond expected variance"
                ],
                "recommendations": [
                    "Consider scaling resources if trend continues",
                    "Review application performance during peak hours"
                ]
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities