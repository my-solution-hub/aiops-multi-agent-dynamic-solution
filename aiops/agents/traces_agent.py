"""Traces Agent for collecting and analyzing AWS X-Ray traces"""

import json
from typing import Dict, List, Any
from .base_tool_agent import BaseToolAgent
from ..orchestrator.base import tool, SystemState


class TracesAgent(BaseToolAgent):
    """Agent specialized in collecting and analyzing AWS X-Ray traces"""
    
    def __init__(self, system_state: SystemState):
        super().__init__(
            agent_id="traces_agent",
            system_state=system_state
        )
        self.capabilities = [
            "xray_traces_collection",
            "trace_analysis",
            "latency_analysis",
            "service_map_generation",
            "bottleneck_detection"
        ]
    
    def get_specialty(self) -> str:
        return "AWS X-Ray traces collection and distributed tracing analysis"
    
    def _get_responsibilities(self) -> str:
        return """- Collect X-Ray traces for distributed applications
- Analyze request latency and performance bottlenecks
- Generate service maps and dependency graphs
- Identify slow or failing service calls
- Provide insights into distributed system performance"""
    
    def get_available_operations(self) -> List[str]:
        return [
            "collect_traces",
            "analyze_latency",
            "detect_bottlenecks",
            "generate_service_map",
            "generate_trace_report"
        ]
    
    def get_tools(self) -> List:
        """Get the tools available to the Traces Agent"""
        return [
            self._collect_traces_tool(),
            self._analyze_latency_tool(),
            self._detect_bottlenecks_tool(),
            self._generate_service_map_tool(),
            self._generate_report_tool()
        ]
    
    def _collect_traces_tool(self):
        """Tool for collecting X-Ray traces"""
        @tool
        def collect_traces(trace_request: str) -> str:
            """Collect X-Ray traces for specified services and time periods.
            
            Args:
                trace_request: JSON string with trace collection parameters
                
            Returns:
                JSON string with collected trace data
            """
            try:
                request = json.loads(trace_request)
                result = self.execute_task("collect_traces", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to collect traces: {str(e)}"})
        
        return collect_traces
    
    def _analyze_latency_tool(self):
        """Tool for analyzing trace latency"""
        @tool
        def analyze_trace_latency(latency_request: str) -> str:
            """Analyze latency patterns in trace data.
            
            Args:
                latency_request: JSON string with latency analysis parameters
                
            Returns:
                JSON string with latency analysis results
            """
            try:
                request = json.loads(latency_request)
                result = self.execute_task("analyze_latency", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to analyze latency: {str(e)}"})
        
        return analyze_trace_latency
    
    def _detect_bottlenecks_tool(self):
        """Tool for detecting performance bottlenecks"""
        @tool
        def detect_bottlenecks(bottleneck_request: str) -> str:
            """Detect performance bottlenecks in distributed traces.
            
            Args:
                bottleneck_request: JSON string with bottleneck detection parameters
                
            Returns:
                JSON string with bottleneck detection results
            """
            try:
                request = json.loads(bottleneck_request)
                result = self.execute_task("detect_bottlenecks", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to detect bottlenecks: {str(e)}"})
        
        return detect_bottlenecks
    
    def _generate_service_map_tool(self):
        """Tool for generating service maps"""
        @tool
        def generate_service_map(map_request: str) -> str:
            """Generate service dependency map from trace data.
            
            Args:
                map_request: JSON string with service map parameters
                
            Returns:
                JSON string with service map data
            """
            try:
                request = json.loads(map_request)
                result = self.execute_task("generate_service_map", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to generate service map: {str(e)}"})
        
        return generate_service_map
    
    def _generate_report_tool(self):
        """Tool for generating trace analysis reports"""
        @tool
        def generate_trace_report(report_request: str) -> str:
            """Generate comprehensive trace analysis report.
            
            Args:
                report_request: JSON string with report generation parameters
                
            Returns:
                JSON string with generated report
            """
            try:
                request = json.loads(report_request)
                result = self.execute_task("generate_trace_report", request)
                return json.dumps(result)
            except Exception as e:
                return json.dumps({"error": f"Failed to generate report: {str(e)}"})
        
        return generate_trace_report
    
    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a traces-related task"""
        if task_description == "collect_traces":
            return self._collect_trace_data(context)
        elif task_description == "analyze_latency":
            return self._analyze_trace_latency(context)
        elif task_description == "detect_bottlenecks":
            return self._detect_trace_bottlenecks(context)
        elif task_description == "generate_service_map":
            return self._generate_service_map(context)
        elif task_description == "generate_trace_report":
            return self._generate_traces_report(context)
        else:
            return {"error": f"Unknown task: {task_description}"}
    
    def _collect_trace_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect X-Ray trace data"""
        # Mock implementation - in real system would use boto3 X-Ray client
        return {
            "status": "success",
            "traces_collected": [
                {
                    "trace_id": "1-5e1b4151-2c4c6b2a1f3d4e5f6a7b8c9d",
                    "duration": 1.25,
                    "response_time": 1250,
                    "services": [
                        {
                            "name": "api-gateway",
                            "duration": 0.05,
                            "response_time": 50
                        },
                        {
                            "name": "lambda-function",
                            "duration": 0.8,
                            "response_time": 800
                        },
                        {
                            "name": "dynamodb",
                            "duration": 0.4,
                            "response_time": 400
                        }
                    ]
                }
            ],
            "collection_time": "2024-01-01T12:15:00Z",
            "total_traces": 1
        }
    
    def _analyze_trace_latency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze latency in trace data"""
        return {
            "status": "success",
            "latency_analysis": {
                "average_latency": 1.25,
                "p95_latency": 2.1,
                "p99_latency": 3.5,
                "slowest_services": [
                    {"service": "lambda-function", "avg_latency": 0.8},
                    {"service": "dynamodb", "avg_latency": 0.4}
                ],
                "latency_trends": {
                    "trend": "increasing",
                    "change_percentage": 15.2
                }
            }
        }
    
    def _detect_trace_bottlenecks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect bottlenecks in trace data"""
        return {
            "status": "success",
            "bottleneck_detection": {
                "bottlenecks_found": 2,
                "critical_bottlenecks": [
                    {
                        "service": "lambda-function",
                        "bottleneck_type": "cpu_intensive_operation",
                        "impact_score": 0.85,
                        "duration_contribution": 0.64
                    },
                    {
                        "service": "dynamodb",
                        "bottleneck_type": "slow_query",
                        "impact_score": 0.72,
                        "duration_contribution": 0.32
                    }
                ],
                "recommendations": [
                    "Optimize Lambda function code for CPU efficiency",
                    "Review DynamoDB query patterns and indexing"
                ]
            }
        }
    
    def _generate_service_map(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service dependency map"""
        return {
            "status": "success",
            "service_map": {
                "services": [
                    {
                        "name": "api-gateway",
                        "type": "gateway",
                        "health": "healthy",
                        "connections": ["lambda-function"]
                    },
                    {
                        "name": "lambda-function", 
                        "type": "compute",
                        "health": "degraded",
                        "connections": ["dynamodb"]
                    },
                    {
                        "name": "dynamodb",
                        "type": "database",
                        "health": "healthy",
                        "connections": []
                    }
                ],
                "dependencies": [
                    {"from": "api-gateway", "to": "lambda-function", "call_count": 100, "error_rate": 0.02},
                    {"from": "lambda-function", "to": "dynamodb", "call_count": 95, "error_rate": 0.05}
                ]
            }
        }
    
    def _generate_traces_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive traces report"""
        return {
            "status": "success",
            "report": {
                "summary": "Trace analysis completed for distributed application",
                "key_findings": [
                    "Lambda function is the primary bottleneck",
                    "DynamoDB queries contributing to latency",
                    "Overall system latency trending upward"
                ],
                "performance_metrics": {
                    "total_requests": 1000,
                    "average_response_time": 1.25,
                    "error_rate": 0.03,
                    "throughput": "800 req/min"
                },
                "recommendations": [
                    "Optimize Lambda function performance",
                    "Implement DynamoDB query optimization",
                    "Consider adding caching layer",
                    "Monitor service dependencies more closely"
                ]
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities