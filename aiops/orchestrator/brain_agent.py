"""Brain Agent implementation using Strands framework for AIOps Root Cause Analysis"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from .base import BaseStrandsAgent, tool, SystemState
from .interfaces import BrainAgentInterface
from ..models.enums import AgentType, InvestigationStatus, ExecutionStatus
from ..models.data_models import (
    AlarmInput, Investigation, InvestigationRound, InvestigationWorkflow,
    WorkflowStep, ExecutionResult, AnalysisReport, RootCause, Evidence
)


class BrainAgent(BaseStrandsAgent, BrainAgentInterface):
    """Brain Agent for AWS alarm analysis and investigation workflow generation"""
    
    def __init__(self, system_state: SystemState):
        super().__init__(
            agent_id="brain_agent",
            agent_type=AgentType.BRAIN,
            system_state=system_state
        )
        self.capabilities = [
            "alarm_analysis",
            "workflow_generation", 
            "report_generation",
            "workflow_adaptation"
        ]
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Brain Agent"""
        return """You are the Brain Agent in an AI Operations system. Your primary responsibilities are:

1. **AWS Alarm Analysis**: Process AWS CloudWatch alarm content to understand the incident context
2. **Investigation Workflow Generation**: Create structured investigation workflows with specific steps for specialized agents
3. **Workflow Adaptation**: Update investigation workflows based on execution results and new findings
4. **Analysis Report Generation**: Create comprehensive analysis reports based on execution results

**Key Principles:**
- Focus on systematic investigation approaches based on alarm characteristics
- Generate specific, actionable workflow steps that can be executed by specialized agents
- Adapt workflows dynamically as new information becomes available
- Maintain investigation context across multiple rounds if needed

**Input Processing:**
- Parse AWS CloudWatch alarm data including metrics, thresholds, and state information
- Identify alarm patterns and categorize incident types
- Consider alarm history and related metrics for context

**Workflow Generation:**
- Create step-by-step investigation plans tailored to the specific alarm type
- Specify required tools and data sources for each step
- Define dependencies between workflow steps

**Response Format:**
- Provide structured JSON responses when generating workflows or reports
- Include clear reasoning for workflow decisions
- Maintain investigation state and context across interactions

Always think systematically and provide detailed reasoning for your analysis and recommendations."""

    def get_tools(self) -> List:
        """Get the tools available to the Brain Agent"""
        return [
            self._create_investigation_tool(),
            self._generate_workflow_tool(),
            self._generate_report_tool(),
            self._update_workflow_tool()
        ]
    
    def _create_investigation_tool(self):
        """Tool for creating new investigations from alarm input"""
        @tool
        def create_investigation(alarm_data: str) -> str:
            """Create a new investigation from AWS alarm data.
            
            Args:
                alarm_data: JSON string containing AWS CloudWatch alarm information
                
            Returns:
                JSON string with investigation details
            """
            try:
                alarm_dict = json.loads(alarm_data)
                alarm_input = AlarmInput(**alarm_dict)
                investigation = self.process_alarm(alarm_input)
                
                return json.dumps({
                    "investigation_id": investigation.investigation_id,
                    "status": investigation.status.value,
                    "alarm_summary": f"{alarm_input.alarm_name}: {alarm_input.alarm_description}",
                    "created_at": investigation.created_at.isoformat()
                })
            except Exception as e:
                return json.dumps({"error": f"Failed to create investigation: {str(e)}"})
        
        return create_investigation
    
    def _generate_workflow_tool(self):
        """Tool for generating investigation workflows"""
        @tool
        def generate_investigation_workflow(investigation_id: str) -> str:
            """Generate investigation workflow for a given investigation.
            
            Args:
                investigation_id: ID of the investigation
                
            Returns:
                JSON string with workflow details
            """
            try:
                investigation = self.get_investigation_context(investigation_id)
                if not investigation:
                    return json.dumps({"error": "Investigation not found"})
                
                workflow = self.generate_workflow(investigation)
                
                return json.dumps({
                    "workflow_id": workflow.workflow_id,
                    "steps": [asdict(step) for step in workflow.steps],
                    "priority": workflow.priority,
                    "estimated_duration": workflow.estimated_duration
                })
            except Exception as e:
                return json.dumps({"error": f"Failed to generate workflow: {str(e)}"})
        
        return generate_investigation_workflow
    

    
    def _generate_report_tool(self):
        """Tool for generating analysis reports"""
        @tool
        def generate_analysis_report(investigation_id: str) -> str:
            """Generate comprehensive analysis report for investigation.
            
            Args:
                investigation_id: ID of the investigation
                
            Returns:
                JSON string with analysis report
            """
            try:
                investigation = self.get_investigation_context(investigation_id)
                if not investigation:
                    return json.dumps({"error": "Investigation not found"})
                
                report = self.generate_analysis_report(investigation)
                
                return json.dumps({
                    "report_id": report.investigation_id,
                    "root_causes": [asdict(rc) for rc in report.root_cause_candidates],
                    "confidence_score": report.confidence_score,
                    "evidence_count": len(report.supporting_evidence),
                    "recommendations": report.recommendations
                })
            except Exception as e:
                return json.dumps({"error": f"Failed to generate report: {str(e)}"})
        
        return generate_analysis_report
    
    def _update_workflow_tool(self):
        """Tool for updating workflows based on execution results"""
        @tool
        def update_investigation_workflow(investigation_id: str, execution_results: str) -> str:
            """Update investigation workflow based on execution results.
            
            Args:
                investigation_id: ID of the investigation
                execution_results: JSON string with execution results
                
            Returns:
                JSON string with updated workflow
            """
            try:
                investigation = self.get_investigation_context(investigation_id)
                if not investigation:
                    return json.dumps({"error": "Investigation not found"})
                
                results_data = json.loads(execution_results)
                execution_results_list = [ExecutionResult(**result) for result in results_data]
                
                # Get current workflow from latest round
                current_round = investigation.rounds[-1] if investigation.rounds else None
                if not current_round or not current_round.workflow:
                    return json.dumps({"error": "No current workflow found"})
                
                updated_workflow = self.update_workflow(current_round.workflow, execution_results_list)
                
                return json.dumps({
                    "workflow_id": updated_workflow.workflow_id,
                    "updated_steps": [asdict(step) for step in updated_workflow.steps],
                    "update_time": datetime.now().isoformat()
                })
            except Exception as e:
                return json.dumps({"error": f"Failed to update workflow: {str(e)}"})
        
        return update_investigation_workflow
    
    def process_alarm(self, alarm_input: AlarmInput) -> Investigation:
        """Process AWS alarm and create initial investigation"""
        investigation_id = str(uuid.uuid4())
        
        investigation = Investigation(
            investigation_id=investigation_id,
            alarm_input=alarm_input,
            rounds=[],
            current_round=0,
            status=InvestigationStatus.INITIATED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add to system state
        self.system_state.add_investigation(investigation)
        
        return investigation
    
    def generate_workflow(self, investigation: Investigation) -> InvestigationWorkflow:
        """Generate investigation workflow based on alarm analysis"""
        alarm = investigation.alarm_input
        workflow_id = str(uuid.uuid4())
        
        # Analyze alarm characteristics to determine workflow steps
        steps = self._create_workflow_steps(alarm)
        
        workflow = InvestigationWorkflow(
            workflow_id=workflow_id,
            steps=steps,
            priority=self._determine_priority(alarm),
            estimated_duration=len(steps) * 5,  # 5 minutes per step estimate
            required_tools=self._extract_required_tools(steps)
        )
        
        # Create new investigation round
        round_id = str(uuid.uuid4())
        investigation_round = InvestigationRound(
            round_id=round_id,
            workflow=workflow,
            execution_results=[],
            analysis_report=None,
            evaluation_result=None,
            start_time=datetime.now(),
            end_time=None
        )
        
        investigation.rounds.append(investigation_round)
        investigation.current_round = len(investigation.rounds) - 1
        self.update_investigation_context(investigation)
        
        return workflow
    
    def _create_workflow_steps(self, alarm: AlarmInput) -> List[WorkflowStep]:
        """Create workflow steps based on alarm characteristics"""
        steps = []
        step_counter = 1
        
        # Basic alarm analysis step
        steps.append(WorkflowStep(
            step_id=f"step_{step_counter}",
            description=f"Analyze {alarm.metric_name} metric behavior and thresholds",
            agent_type="metrics_agent",
            required_data=["cloudwatch_metrics", "alarm_history"],
            expected_output="metric_analysis_report",
            dependencies=[]
        ))
        step_counter += 1
        
        # Resource-specific steps based on namespace
        if alarm.namespace == "AWS/EC2":
            steps.append(WorkflowStep(
                step_id=f"step_{step_counter}",
                description="Check EC2 instance health and system metrics",
                agent_type="system_agent",
                required_data=["instance_status", "system_logs"],
                expected_output="instance_health_report",
                dependencies=[f"step_{step_counter-1}"]
            ))
            step_counter += 1
            
        elif alarm.namespace == "AWS/RDS":
            steps.append(WorkflowStep(
                step_id=f"step_{step_counter}",
                description="Analyze database performance and connection metrics",
                agent_type="database_agent",
                required_data=["db_performance_insights", "connection_logs"],
                expected_output="database_analysis_report",
                dependencies=[f"step_{step_counter-1}"]
            ))
            step_counter += 1
            
        elif alarm.namespace == "AWS/ApplicationELB":
            steps.append(WorkflowStep(
                step_id=f"step_{step_counter}",
                description="Check load balancer health and target group status",
                agent_type="network_agent",
                required_data=["elb_metrics", "target_health"],
                expected_output="load_balancer_report",
                dependencies=[f"step_{step_counter-1}"]
            ))
            step_counter += 1
        
        # Log analysis step
        steps.append(WorkflowStep(
            step_id=f"step_{step_counter}",
            description="Analyze application and system logs for error patterns",
            agent_type="logs_agent",
            required_data=["application_logs", "system_logs"],
            expected_output="log_analysis_report",
            dependencies=[f"step_{step_counter-1}"]
        ))
        
        return steps
    
    def _determine_priority(self, alarm: AlarmInput) -> str:
        """Determine investigation priority based on alarm characteristics"""
        if alarm.alarm_state == "ALARM":
            if "critical" in alarm.alarm_description.lower() or "error" in alarm.alarm_description.lower():
                return "HIGH"
            else:
                return "MEDIUM"
        return "LOW"
    
    def _extract_required_tools(self, steps: List[WorkflowStep]) -> List[str]:
        """Extract required tools from workflow steps"""
        tools = set()
        for step in steps:
            if step.agent_type == "metrics_agent":
                tools.add("cloudwatch_client")
            elif step.agent_type == "logs_agent":
                tools.add("logs_client")
            elif step.agent_type == "network_agent":
                tools.add("elb_client")
            elif step.agent_type == "system_agent":
                tools.add("ec2_client")
        return list(tools)
    
    def update_workflow(self, workflow: InvestigationWorkflow, 
                       execution_results: List[ExecutionResult]) -> InvestigationWorkflow:
        """Update workflow based on execution results"""
        # Analyze execution results to determine if workflow needs updates
        failed_steps = [result for result in execution_results if result.status == ExecutionStatus.FAILED]
        
        if failed_steps:
            # Add retry or alternative steps for failed ones
            for failed_result in failed_steps:
                retry_step = WorkflowStep(
                    step_id=f"{failed_result.step_id}_retry",
                    description=f"Retry: {failed_result.step_id}",
                    agent_type="general_agent",
                    required_data=["previous_results"],
                    expected_output="retry_analysis",
                    dependencies=[]
                )
                workflow.steps.append(retry_step)
        
        # Check if additional investigation steps are needed based on findings
        for result in execution_results:
            if result.next_recommended_steps:
                for rec_step in result.next_recommended_steps:
                    additional_step = WorkflowStep(
                        step_id=f"additional_{len(workflow.steps) + 1}",
                        description=rec_step,
                        agent_type="specialized_agent",
                        required_data=["context_data"],
                        expected_output="additional_analysis",
                        dependencies=[result.step_id]
                    )
                    workflow.steps.append(additional_step)
        
        return workflow
    

    
    def generate_analysis_report(self, investigation: Investigation) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        if not investigation.rounds:
            raise ValueError("No investigation rounds available for report generation")
        
        current_round = investigation.rounds[-1]
        
        # Extract root cause candidates from execution results
        root_causes = self._extract_root_causes(current_round.execution_results)
        
        # Compile supporting evidence
        evidence = self._compile_evidence(current_round.execution_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(root_causes, evidence)
        
        # Simple confidence calculation for report
        confidence_score = 0.8 if root_causes else 0.3  # Basic threshold
        
        report = AnalysisReport(
            investigation_id=investigation.investigation_id,
            root_cause_candidates=root_causes,
            supporting_evidence=evidence,
            confidence_score=confidence_score,
            investigation_timeline=[],  # TODO: Implement timeline extraction
            recommendations=recommendations
        )
        
        current_round.analysis_report = report
        self.update_investigation_context(investigation)
        
        return report
    
    def _extract_root_causes(self, execution_results: List[ExecutionResult]) -> List[RootCause]:
        """Extract root cause candidates from execution results"""
        root_causes = []
        
        for result in execution_results:
            if result.status == ExecutionStatus.COMPLETED and result.confidence_score > 0.6:
                # Extract potential root causes from findings
                findings = result.findings
                if "root_cause" in findings:
                    root_cause = RootCause(
                        cause_id=str(uuid.uuid4()),
                        description=findings["root_cause"],
                        probability=result.confidence_score,
                        supporting_evidence=[result.step_id],
                        mitigation_steps=findings.get("mitigation", [])
                    )
                    root_causes.append(root_cause)
        
        return root_causes
    
    def _compile_evidence(self, execution_results: List[ExecutionResult]) -> List[Evidence]:
        """Compile supporting evidence from execution results"""
        evidence = []
        
        for result in execution_results:
            if result.status == ExecutionStatus.COMPLETED:
                evidence_item = Evidence(
                    evidence_id=str(uuid.uuid4()),
                    type="execution_result",
                    source=result.step_id,
                    content=result.findings,
                    reliability_score=result.confidence_score,
                    timestamp=datetime.now()
                )
                evidence.append(evidence_item)
        
        return evidence
    
    def _generate_recommendations(self, root_causes: List[RootCause], 
                                evidence: List[Evidence]) -> List[str]:
        """Generate recommendations based on root causes and evidence"""
        recommendations = []
        
        if root_causes:
            for cause in root_causes:
                recommendations.extend(cause.mitigation_steps)
        else:
            recommendations.append("Continue investigation with additional data collection")
            recommendations.append("Review alarm thresholds and configuration")
            recommendations.append("Implement enhanced monitoring for early detection")
        
        return recommendations
    
    def process_consolidated_facts(self, investigation: Investigation, 
                                 consolidated_facts: dict) -> InvestigationWorkflow:
        """Process consolidated facts and generate new investigation round"""
        # Create new workflow based on consolidated facts
        workflow_id = str(uuid.uuid4())
        
        # Generate steps based on gaps identified in consolidated facts
        steps = self._create_followup_steps(consolidated_facts)
        
        workflow = InvestigationWorkflow(
            workflow_id=workflow_id,
            steps=steps,
            priority="MEDIUM",
            estimated_duration=len(steps) * 5,
            required_tools=self._extract_required_tools(steps)
        )
        
        # Create new investigation round
        round_id = str(uuid.uuid4())
        investigation_round = InvestigationRound(
            round_id=round_id,
            workflow=workflow,
            execution_results=[],
            analysis_report=None,
            evaluation_result=None,
            start_time=datetime.now(),
            end_time=None
        )
        
        investigation.rounds.append(investigation_round)
        investigation.current_round = len(investigation.rounds) - 1
        self.update_investigation_context(investigation)
        
        return workflow
    
    def _create_followup_steps(self, consolidated_facts: dict) -> List[WorkflowStep]:
        """Create follow-up investigation steps based on consolidated facts"""
        steps = []
        step_counter = 1
        
        # Analyze gaps in consolidated facts
        if "missing_metrics" in consolidated_facts:
            steps.append(WorkflowStep(
                step_id=f"followup_{step_counter}",
                description="Collect missing metric data identified in previous round",
                agent_type="metrics_agent",
                required_data=consolidated_facts["missing_metrics"],
                expected_output="additional_metrics_report",
                dependencies=[]
            ))
            step_counter += 1
        
        if "unresolved_patterns" in consolidated_facts:
            steps.append(WorkflowStep(
                step_id=f"followup_{step_counter}",
                description="Investigate unresolved patterns from previous analysis",
                agent_type="pattern_agent",
                required_data=["pattern_data", "historical_data"],
                expected_output="pattern_analysis_report",
                dependencies=[]
            ))
            step_counter += 1
        
        return steps
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities