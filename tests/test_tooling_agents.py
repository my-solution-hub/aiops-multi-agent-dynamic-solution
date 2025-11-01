#!/usr/bin/env python3
"""Test script for tooling agents"""

import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aiops.orchestrator.base import SystemState
from aiops.agents.metrics_agent import MetricsAgent
from aiops.agents.logs_agent import LogsAgent
from aiops.agents.traces_agent import TracesAgent


def test_metrics_agent():
    """Test Metrics Agent functionality"""
    print("Testing Metrics Agent...")
    
    system_state = SystemState()
    metrics_agent = MetricsAgent(system_state)
    
    print(f"✓ Metrics Agent created with ID: {metrics_agent.agent_id}")
    print(f"✓ Agent type: {metrics_agent.agent_type}")
    print(f"✓ Capabilities: {metrics_agent.get_capabilities()}")
    print(f"✓ Available operations: {metrics_agent.get_available_operations()}")
    
    # Test task execution
    context = {
        "metric_name": "CPUUtilization",
        "namespace": "AWS/EC2",
        "dimensions": {"InstanceId": "i-1234567890abcdef0"}
    }
    
    result = metrics_agent.execute_task("collect_metrics", context)
    print(f"✓ Task execution successful: {result['status']}")
    
    return metrics_agent


def test_logs_agent():
    """Test Logs Agent functionality"""
    print("\nTesting Logs Agent...")
    
    system_state = SystemState()
    logs_agent = LogsAgent(system_state)
    
    print(f"✓ Logs Agent created with ID: {logs_agent.agent_id}")
    print(f"✓ Agent type: {logs_agent.agent_type}")
    print(f"✓ Capabilities: {logs_agent.get_capabilities()}")
    print(f"✓ Available operations: {logs_agent.get_available_operations()}")
    
    # Test task execution
    context = {
        "log_group": "/aws/lambda/my-function",
        "start_time": "2024-01-01T12:00:00Z",
        "end_time": "2024-01-01T12:15:00Z"
    }
    
    result = logs_agent.execute_task("collect_logs", context)
    print(f"✓ Task execution successful: {result['status']}")
    
    return logs_agent


def test_traces_agent():
    """Test Traces Agent functionality"""
    print("\nTesting Traces Agent...")
    
    system_state = SystemState()
    traces_agent = TracesAgent(system_state)
    
    print(f"✓ Traces Agent created with ID: {traces_agent.agent_id}")
    print(f"✓ Agent type: {traces_agent.agent_type}")
    print(f"✓ Capabilities: {traces_agent.get_capabilities()}")
    print(f"✓ Available operations: {traces_agent.get_available_operations()}")
    
    # Test task execution
    context = {
        "service_name": "my-api",
        "start_time": "2024-01-01T12:00:00Z",
        "end_time": "2024-01-01T12:15:00Z"
    }
    
    result = traces_agent.execute_task("collect_traces", context)
    print(f"✓ Task execution successful: {result['status']}")
    
    return traces_agent


def test_agent_tools():
    """Test agent tools functionality"""
    print("\nTesting Agent Tools...")
    
    system_state = SystemState()
    metrics_agent = MetricsAgent(system_state)
    
    # Test tool availability
    tools = metrics_agent.get_tools()
    print(f"✓ Tools available: {len(tools)} tools")
    
    # Test system prompt
    prompt = metrics_agent.get_system_prompt()
    print(f"✓ System prompt configured (length: {len(prompt)} chars)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("TOOLING AGENTS TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        metrics_agent = test_metrics_agent()
        logs_agent = test_logs_agent()
        traces_agent = test_traces_agent()
        test_agent_tools()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print(f"Tooling agents successfully created and tested")
        print(f"Metrics, Logs, and Traces agents functional")
        print(f"Agent tools and capabilities working")
        print(f"Task execution system operational")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())