#!/usr/bin/env python3
"""Interactive CLI for testing Strands-based Brain Agent"""

import json
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aiops.orchestrator.brain_agent import BrainAgent
from aiops.orchestrator.base import SystemState
from aiops.models.data_models import AlarmInput


def create_sample_alarms():
    """Create sample alarm scenarios"""
    return {
        "1": {
            "name": "High CPU Utilization",
            "data": {
                "alarm_name": "HighCPUUtilization",
                "alarm_description": "CPU utilization is above 80% for EC2 instance",
                "metric_name": "CPUUtilization",
                "namespace": "AWS/EC2",
                "dimensions": {"InstanceId": "i-1234567890abcdef0"},
                "threshold": 80.0,
                "comparison_operator": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "datapoints_to_alarm": 2,
                "alarm_state": "ALARM",
                "state_reason": "Threshold Crossed: 2 out of the last 2 datapoints were greater than the threshold (80.0).",
                "timestamp": datetime.now().isoformat(),
                "region": "us-east-1"
            }
        },
        "2": {
            "name": "Database Connection Failure",
            "data": {
                "alarm_name": "DatabaseConnectionFailure",
                "alarm_description": "Database connection failures detected",
                "metric_name": "DatabaseConnections",
                "namespace": "AWS/RDS",
                "dimensions": {"DBInstanceIdentifier": "mydb-instance"},
                "threshold": 10.0,
                "comparison_operator": "LessThanThreshold",
                "evaluation_periods": 1,
                "datapoints_to_alarm": 1,
                "alarm_state": "ALARM",
                "state_reason": "Database connections dropped below threshold",
                "timestamp": datetime.now().isoformat(),
                "region": "us-east-1"
            }
        },
        "3": {
            "name": "Load Balancer High Latency",
            "data": {
                "alarm_name": "ELBHighLatency",
                "alarm_description": "Application Load Balancer response time is high",
                "metric_name": "TargetResponseTime",
                "namespace": "AWS/ApplicationELB",
                "dimensions": {"LoadBalancer": "app/my-load-balancer/50dc6c495c0c9188"},
                "threshold": 2.0,
                "comparison_operator": "GreaterThanThreshold",
                "evaluation_periods": 3,
                "datapoints_to_alarm": 2,
                "alarm_state": "ALARM",
                "state_reason": "Response time exceeded 2 seconds",
                "timestamp": datetime.now().isoformat(),
                "region": "us-west-2"
            }
        }
    }


def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("STRANDS BRAIN AGENT - INTERACTIVE CLI")
    print("=" * 60)
    print("1. Process Sample Alarm")
    print("2. Generate Investigation Workflow")
    print("3. Generate Analysis Report")
    print("4. View System State")
    print("5. View Agent Capabilities")
    print("6. Exit")
    print("-" * 60)


def process_sample_alarm(brain_agent, sample_alarms):
    """Process a sample alarm"""
    print("\nAvailable Sample Alarms:")
    for key, alarm in sample_alarms.items():
        print(f"{key}. {alarm['name']}")
    
    choice = input("\nSelect alarm (1-3): ").strip()
    
    if choice not in sample_alarms:
        print("Invalid choice!")
        return None
    
    alarm_data = sample_alarms[choice]["data"]
    alarm_input = AlarmInput(**alarm_data)
    
    print(f"\nProcessing alarm: {alarm_data['alarm_name']}")
    print(f"Description: {alarm_data['alarm_description']}")
    
    investigation = brain_agent.process_alarm(alarm_input)
    
    print(f"\n✓ Investigation created!")
    print(f"  ID: {investigation.investigation_id}")
    print(f"  Status: {investigation.status}")
    print(f"  Created: {investigation.created_at}")
    
    return investigation


def generate_workflow(brain_agent, system_state):
    """Generate workflow for an investigation"""
    investigations = system_state.active_investigations
    
    if not investigations:
        print("\nNo active investigations found. Please process an alarm first.")
        return None
    
    print("\nActive Investigations:")
    inv_list = list(investigations.items())
    for i, (inv_id, inv) in enumerate(inv_list, 1):
        print(f"{i}. {inv.alarm_input.alarm_name} ({inv_id[:8]}...)")
    
    try:
        choice = int(input(f"\nSelect investigation (1-{len(inv_list)}): ")) - 1
        if choice < 0 or choice >= len(inv_list):
            print("Invalid choice!")
            return None
        
        investigation = inv_list[choice][1]
        
        print(f"\nGenerating workflow for: {investigation.alarm_input.alarm_name}")
        workflow = brain_agent.generate_workflow(investigation)
        
        print(f"\n✓ Workflow generated!")
        print(f"  ID: {workflow.workflow_id}")
        print(f"  Priority: {workflow.priority}")
        print(f"  Estimated Duration: {workflow.estimated_duration} minutes")
        print(f"  Steps: {len(workflow.steps)}")
        
        print(f"\nWorkflow Steps:")
        for i, step in enumerate(workflow.steps, 1):
            print(f"  {i}. {step.description}")
            print(f"     Agent: {step.agent_type}")
            print(f"     Required Data: {', '.join(step.required_data)}")
            print(f"     Dependencies: {', '.join(step.dependencies) if step.dependencies else 'None'}")
            print()
        
        return workflow
        
    except ValueError:
        print("Invalid input!")
        return None


def generate_analysis_report(brain_agent, system_state):
    """Generate analysis report for an investigation"""
    investigations = system_state.active_investigations
    
    if not investigations:
        print("\nNo active investigations found.")
        return None
    
    print("\nActive Investigations:")
    inv_list = list(investigations.items())
    for i, (inv_id, inv) in enumerate(inv_list, 1):
        print(f"{i}. {inv.alarm_input.alarm_name} ({inv_id[:8]}...)")
    
    try:
        choice = int(input(f"\nSelect investigation (1-{len(inv_list)}): ")) - 1
        if choice < 0 or choice >= len(inv_list):
            print("Invalid choice!")
            return None
        
        investigation = inv_list[choice][1]
        
        print(f"\nGenerating analysis report for: {investigation.alarm_input.alarm_name}")
        
        try:
            report = brain_agent.generate_analysis_report(investigation)
            
            print(f"\n✓ Analysis Report Generated:")
            print(f"  Investigation ID: {report.investigation_id}")
            print(f"  Confidence Score: {report.confidence_score:.2f}")
            print(f"  Root Cause Candidates: {len(report.root_cause_candidates)}")
            print(f"  Supporting Evidence: {len(report.supporting_evidence)}")
            print(f"  Recommendations: {len(report.recommendations)}")
            
            if report.recommendations:
                print(f"\n  Recommendations:")
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"    {i}. {rec}")
            
            return report
        except Exception as e:
            print(f"\n⚠️  Report generation failed: {str(e)}")
            return None
        
    except ValueError:
        print("Invalid input!")
        return None


def view_system_state(system_state):
    """View current system state"""
    print(f"\n📊 System State Overview:")
    print(f"  Active Investigations: {len(system_state.active_investigations)}")
    print(f"  Registered Agents: {len(system_state.agent_states)}")
    print(f"  Workflow Templates: {len(system_state.workflow_templates)}")
    
    if system_state.active_investigations:
        print(f"\n🔍 Active Investigations:")
        for inv_id, inv in system_state.active_investigations.items():
            print(f"  • {inv.alarm_input.alarm_name} ({inv_id[:8]}...)")
            print(f"    Status: {inv.status}")
            print(f"    Rounds: {len(inv.rounds)}")
            print(f"    Created: {inv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if system_state.agent_states:
        print(f"\n🤖 Registered Agents:")
        for agent_id, agent_state in system_state.agent_states.items():
            print(f"  • {agent_id} ({agent_state.agent_type.value})")
            print(f"    Active: {agent_state.is_active}")
            print(f"    Load: {agent_state.load_level:.1%}")
            print(f"    Current Task: {agent_state.current_task or 'None'}")


def view_agent_capabilities(brain_agent):
    """View agent capabilities"""
    print(f"\n🧠 Brain Agent Capabilities:")
    capabilities = brain_agent.get_capabilities()
    for i, capability in enumerate(capabilities, 1):
        print(f"  {i}. {capability}")
    
    print(f"\n🛠️ Available Tools:")
    tools = brain_agent.get_tools()
    for i, tool in enumerate(tools, 1):
        tool_name = "Unknown"
        if hasattr(tool, '__name__'):
            tool_name = tool.__name__
        elif hasattr(tool, 'func') and hasattr(tool.func, '__name__'):
            tool_name = tool.func.__name__
        print(f"  {i}. {tool_name}")
    
    print(f"\n📝 System Prompt Preview:")
    prompt = brain_agent.get_system_prompt()
    print(f"  Length: {len(prompt)} characters")
    print(f"  Preview: {prompt[:200]}...")


def main():
    """Main CLI loop"""
    print("Initializing Strands Brain Agent...")
    
    # Initialize system
    system_state = SystemState()
    brain_agent = BrainAgent(system_state)
    sample_alarms = create_sample_alarms()
    
    print("✓ Brain Agent initialized successfully!")
    
    while True:
        display_menu()
        choice = input("Select option (1-6): ").strip()
        
        try:
            if choice == "1":
                process_sample_alarm(brain_agent, sample_alarms)
            elif choice == "2":
                generate_workflow(brain_agent, system_state)
            elif choice == "3":
                generate_analysis_report(brain_agent, system_state)
            elif choice == "4":
                view_system_state(system_state)
            elif choice == "5":
                view_agent_capabilities(brain_agent)
            elif choice == "6":
                print("\nGoodbye! 👋")
                break
            else:
                print("Invalid choice! Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\nExiting... 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()