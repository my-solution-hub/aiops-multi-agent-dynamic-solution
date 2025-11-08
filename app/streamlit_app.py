#!/usr/bin/env python3
"""Streamlit app for AIOps investigation monitoring and triggering."""

import streamlit as st
import boto3
import json
import time
from datetime import datetime, timedelta
import os

# AWS clients
bedrock_agentcore = boto3.client('bedrock-agentcore')
dynamodb = boto3.resource('dynamodb')
logs_client = boto3.client('logs')

# Configuration from environment
AGENT_RUNTIME_ARN = os.getenv('AGENT_RUNTIME_ARN', '')
INVESTIGATIONS_TABLE = os.getenv('INVESTIGATIONS_TABLE', 'aiops-investigations')
CONTEXT_TABLE = os.getenv('CONTEXT_TABLE', 'aiops-investigation-context')
LOG_GROUP = os.getenv('AGENTCORE_LOG_GROUP', '/aws/bedrock-agentcore/runtime')

st.set_page_config(page_title="AIOps Monitor", layout="wide")
st.title("🔍 AIOps Investigation Monitor")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    runtime_arn = st.text_input("Agent Runtime ARN", value=AGENT_RUNTIME_ARN)
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    st.divider()
    st.header("Tables")
    st.text(f"Workflow: {INVESTIGATIONS_TABLE}")
    st.text(f"Context: {CONTEXT_TABLE}")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🚀 Trigger", "📊 Investigations", "📝 Logs"])

# Tab 1: Trigger Investigation
with tab1:
    st.header("Trigger New Investigation")
    
    alarm_input = st.text_area(
        "Alarm Content (multi-line)",
        height=200,
        placeholder="Paste CloudWatch alarm JSON or text here..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Trigger", type="primary"):
            if not alarm_input:
                st.error("Please provide alarm content")
            elif not runtime_arn:
                st.error("Please configure Agent Runtime ARN")
            else:
                with st.spinner("Triggering investigation..."):
                    try:
                        payload = json.dumps({"alarm": alarm_input})
                        
                        response = bedrock_agentcore.invoke_agent_runtime(
                            agentRuntimeArn=runtime_arn,
                            qualifier='DEFAULT',
                            payload=payload.encode('utf-8')
                        )
                        
                        # Response is dict with StreamingBody
                        result = json.loads(response['response'].read())
                        print(result)
                        
                        st.success(f"✅ Investigation triggered: {result.get('investigation_id', 'N/A')}")
                        st.json(result)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 2: Investigation Status
with tab2:
    st.header("Investigation Status")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get investigations
    try:
        workflow_table = dynamodb.Table(INVESTIGATIONS_TABLE)
        context_table = dynamodb.Table(CONTEXT_TABLE)
        
        # Scan workflow table for metadata
        response = workflow_table.scan(
            FilterExpression='item_type = :type',
            ExpressionAttributeValues={':type': 'METADATA'},
            Limit=20
        )
        
        investigations = response.get('Items', [])
        
        if investigations:
            for inv in sorted(investigations, key=lambda x: x.get('created_at', ''), reverse=True):
                inv_id = inv['investigation_id']
                
                with st.expander(f"📋 {inv_id} - {inv.get('status', 'UNKNOWN')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Workflow")
                        st.json({
                            "status": inv.get('status'),
                            "created_at": inv.get('created_at'),
                            "alarm_summary": inv.get('alarm_summary', {}),
                            "execution_plan": inv.get('execution_plan', {})
                        })
                    
                    with col2:
                        st.subheader("Context")
                        try:
                            ctx_response = context_table.get_item(Key={'investigation_id': inv_id})
                            if 'Item' in ctx_response:
                                ctx = ctx_response['Item']
                                st.json({
                                    "confidence": ctx.get('confidence', 0),
                                    "hypothesis": ctx.get('current_hypothesis', ''),
                                    "findings": ctx.get('findings', {}),
                                    "timeline": ctx.get('timeline', [])
                                })
                            else:
                                st.info("No context found")
                        except Exception as e:
                            st.error(f"Error loading context: {e}")
        else:
            st.info("No investigations found")
            
    except Exception as e:
        st.error(f"Error loading investigations: {str(e)}")

# Tab 3: CloudWatch Logs
with tab3:
    st.header("AgentCore Runtime Logs")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        minutes = st.number_input("Minutes back", min_value=1, max_value=60, value=15)
    with col2:
        filter_pattern = st.text_input("Filter pattern", value="")
    with col3:
        if st.button("📝 Fetch Logs"):
            st.rerun()
    
    try:
        start_time = int((datetime.now() - timedelta(minutes=minutes)).timestamp() * 1000)
        end_time = int(datetime.now().timestamp() * 1000)
        
        kwargs = {
            'logGroupName': LOG_GROUP,
            'startTime': start_time,
            'endTime': end_time,
            'limit': 100
        }
        
        if filter_pattern:
            kwargs['filterPattern'] = filter_pattern
        
        response = logs_client.filter_log_events(**kwargs)
        events = response.get('events', [])
        
        if events:
            st.info(f"Found {len(events)} log entries")
            for event in reversed(events):
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                st.text(f"[{timestamp.strftime('%H:%M:%S')}] {event['message']}")
        else:
            st.info("No logs found")
            
    except Exception as e:
        st.error(f"Error fetching logs: {str(e)}")

# Auto-refresh
if auto_refresh:
    time.sleep(5)
    st.rerun()
