#!/usr/bin/env python3
"""Test script for AgentCore Gateway - Fixed version"""

import boto3
import json

def get_gateway_arn():
    """Get the Gateway ARN from CloudFormation outputs"""
    cf_client = boto3.client('cloudformation')
    
    try:
        response = cf_client.describe_stacks(StackName='AIOpsStack')
        outputs = response['Stacks'][0]['Outputs']
        
        for output in outputs:
            if output['OutputKey'] == 'AgentCoreGatewayArn':
                arn = output['OutputValue']
                print(f"Found Gateway ARN: {arn}")
                return arn
    except Exception as e:
        print(f"Error getting Gateway ARN: {e}")
        return None

def check_gateway_status():
    """Check if Gateway exists and is active"""
    
    gateway_arn = get_gateway_arn()
    if not gateway_arn:
        return False
    
    try:
        client = boto3.client('bedrock-agentcore-control')
        gateway_id = gateway_arn.split('/')[-1]
        
        print(f"Gateway ID: {gateway_id}")
        
        response = client.get_gateway(gatewayIdentifier=gateway_id)

        gateway = response
        
        # Extract only the fields we need to avoid datetime serialization issues
        status = gateway.get('status', 'UNKNOWN')
        name = gateway.get('name', 'Unknown')
        protocol = gateway.get('protocolType', 'Unknown')
        
        print(f"Gateway Name: {name}")
        print(f"Gateway Status: {status}")
        print(f"Protocol Type: {protocol}")
        
        if status in ['ACTIVE', 'AVAILABLE', 'READY']:
            print("✅ Gateway is ready!")
            return True
        else:
            print(f"❌ Gateway status is: {status}")
            return False
        
    except Exception as e:
        print(f"Error checking Gateway status: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking AgentCore Gateway...")
    check_gateway_status()
