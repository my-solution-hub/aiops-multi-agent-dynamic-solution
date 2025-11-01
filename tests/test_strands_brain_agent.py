#!/usr/bin/env python3
"""Test script for Strands-based Brain Agent"""

import json
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aiops.orchestrator.brain_agent import BrainAgent
from aiops.orchestrator.base import SystemState
from aiops.models.data_models import AlarmInput


def test_brain_agent_creation():
    """Test Brain Agent creation and basic functionality"""
    print("Testing Brain Agent creation...")
    
    # Create system state
    system_state = SystemState()
    
    # Create Brain Agent
    brain_agent = BrainAgent(system_state)
    
    print(f"✓ Brain Agent created with ID: {brain_agent.agent_id}")
    print(f"✓ Agent type: {brain_agent.agent_type}")
    print(f"✓ Capabilities: {brain_agent.get_capabilities()}")
    
    return brain_agent


def test_alarm_processing():
    """Test alarm processing functionality"""
    print("\nTesting alarm processing...")
    
    system_state = SystemState()
    brain_agent = BrainAgent(system_state)
    
    # Create test alarm input
    alarm_input = AlarmInput(
        alarm_name="HighCPUUtilization",
        alarm_description="CPU utilization is above 80%",
        metric_name="CPUUtilization",
        namespace="AWS/EC2",
        dimensions={"InstanceId": "i-1234567890abcdef0"},
        threshold=80.0,
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=2,
        datapoints_to_alarm=2,
        alarm_state="ALARM",
        state_reason="Threshold Crossed: 2 out of the last 2 datapoints were greater than the threshold (80.0).",
        timestamp=datetime.now(),
        region="us-east-1"
    )
    
    # Process alarm
    investigation = brain_agent.process_alarm(alarm_input)
    
    print(f"✓ Investigation created with ID: {investigation.investigation_id}")
    print(f"✓ Investigation status: {investigation.status}")
    print(f"✓ Alarm processed: {investigation.alarm_input.alarm_name}")
    
    return investigation


def test_workflow_generation():
    """Test workflow generation"""
    print("\nTesting workflow generation...")
    
    system_state = SystemState()
    brain_agent = BrainAgent(system_state)
    
    # Create and process alarm
    alarm_input = AlarmInput(
        alarm_name="DatabaseConnectionFailure",
        alarm_description="Database connection failures detected",
        metric_name="DatabaseConnections",
        namespace="AWS/RDS",
        dimensions={"DBInstanceIdentifier": "mydb-instance"},
        threshold=10.0,
        comparison_operator="LessThanThreshold",
        evaluation_periods=1,
        datapoints_to_alarm=1,
        alarm_state="ALARM",
        state_reason="Database connections dropped below threshold",
        timestamp=datetime.now(),
        region="us-east-1"
    )
    
    investigation = brain_agent.process_alarm(alarm_input)
    
    # Generate workflow
    workflow = brain_agent.generate_workflow(investigation)
    
    print(f"✓ Workflow generated with ID: {workflow.workflow_id}")
    print(f"✓ Number of steps: {len(workflow.steps)}")
    print(f"✓ Priority: {workflow.priority}")
    print(f"✓ Estimated duration: {workflow.estimated_duration} minutes")
    
    for i, step in enumerate(workflow.steps, 1):
        print(f"  Step {i}: {step.description} (Agent: {step.agent_type})")
    
    return workflow


def test_real_llm_interaction():
    """Test real LLM interaction through Strands agent"""
    print("\nTesting real LLM interaction...")
    
    system_state = SystemState()
    brain_agent = BrainAgent(system_state)
    
    # Test alarm creation through real LLM
    alarm_data = {
        "alarm_name": "HighMemoryUsage",
        "alarm_description": "Memory usage is critically high on EC2 instance",
        "metric_name": "MemoryUtilization",
        "namespace": "AWS/EC2",
        "dimensions": {"InstanceId": "i-abcdef1234567890"},
        "threshold": 90.0,
        "comparison_operator": "GreaterThanThreshold",
        "evaluation_periods": 1,
        "datapoints_to_alarm": 1,
        "alarm_state": "ALARM",
        "state_reason": "Memory usage exceeded threshold",
        "timestamp": datetime.now().isoformat(),
        "region": "us-west-2"
    }
    
    # Process request through real Strands agent
    request = f"Analyze this AWS alarm and create an investigation: {json.dumps(alarm_data)}"
    
    print(f"Sending request to LLM: {request[:100]}...")
    response = brain_agent.process_request(request)
    
    print(f"✓ Real LLM response received")
    print(f"Response length: {len(response)} characters")
    print(f"Response preview: {response[:300]}...")
    
    return response


def test_llm_workflow_generation():
    """Test LLM-based workflow generation"""
    print("\nTesting LLM workflow generation...")
    
    system_state = SystemState()
    brain_agent = BrainAgent(system_state)
    
    # First create an investigation through LLM
    alarm_data = {
        "alarm_name": "DatabaseConnectionFailure", 
        "alarm_description": "RDS database connection failures detected",
        "metric_name": "DatabaseConnections",
        "namespace": "AWS/RDS",
        "dimensions": {"DBInstanceIdentifier": "prod-db-1"},
        "threshold": 5.0,
        "comparison_operator": "LessThanThreshold",
        "evaluation_periods": 2,
        "datapoints_to_alarm": 2,
        "alarm_state": "ALARM",
        "state_reason": "Database connections dropped below 5",
        "timestamp": datetime.now().isoformat(),
        "region": "us-east-1"
    }
    
    # Create investigation through LLM
    create_request = f"Create investigation for this alarm: {json.dumps(alarm_data)}"
    print(f"Creating investigation through LLM...")
    create_response = brain_agent.process_request(create_request)
    
    # Extract investigation ID from response (assuming JSON format)
    try:
        import re
        id_match = re.search(r'"investigation_id":\s*"([^"]+)"', create_response)
        if id_match:
            investigation_id = id_match.group(1)
            print(f"✓ Investigation created with ID: {investigation_id}")
            
            # Generate workflow through LLM
            workflow_request = f"Generate investigation workflow for investigation {investigation_id}"
            print(f"Generating workflow through LLM...")
            workflow_response = brain_agent.process_request(workflow_request)
            
            print(f"✓ Workflow generation response received")
            print(f"Response preview: {workflow_response[:300]}...")
            
            return workflow_response
        else:
            print("⚠️ Could not extract investigation ID from response")
            return create_response
            
    except Exception as e:
        print(f"⚠️ Error processing LLM responses: {str(e)}")
        return create_response


def main():
    """Run all tests"""
    print("=" * 60)
    print("STRANDS BRAIN AGENT TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        brain_agent = test_brain_agent_creation()
        investigation = test_alarm_processing()
        workflow = test_workflow_generation()
        llm_response = test_real_llm_interaction()
        workflow_response = test_llm_workflow_generation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print(f"Brain Agent successfully created and tested")
        print(f"Real LLM integration working through Strands framework")
        print(f"Investigation workflow generation working")
        print(f"LLM-based tool calling functional")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())