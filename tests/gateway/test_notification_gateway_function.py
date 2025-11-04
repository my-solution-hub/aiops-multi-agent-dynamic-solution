from strands.models import BedrockModel
import time
import boto3
import utils
import os
import sys

## The IAM credentials configured in ~/.aws/credentials should have access to Bedrock model
yourmodel = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
)

from strands import Agent
import logging
from strands import Agent
import logging
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client 
from botocore.credentials import Credentials
from streamable_http_sigv4 import (
    streamablehttp_client_with_sigv4,
)

SERVICE="bedrock-agentcore"

# Configure the root strands logger. Change it to DEBUG if you are debugging the issue.
logging.getLogger("strands").setLevel(logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

def create_streamable_http_transport(mcp_url: str, access_token: str):
       return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})

def create_streamable_http_transport_sigv4(mcp_url: str, key: str, secret: str, serviceName: str, awsRegion: str):
        iamcredentials = Credentials(
            access_key=key,
            secret_key=secret
        )
        return streamablehttp_client_with_sigv4(
            url=mcp_url,
            credentials=iamcredentials,
            service=serviceName,
            region=awsRegion,
        )

def get_full_tools_list(client):
    more_tools = True
    tools = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True 
            pagination_token = tmp_tools.pagination_token
    return tools

def call_tool_sync(client, tool_id,tool_name, parameters=None):
    # Call the tool (no pagination argument supported)
    response = client.call_tool_sync(
        tool_use_id=tool_id,
        name=tool_name,
        arguments=parameters
    )

    # Extract output content
    if hasattr(response, "results") and response.results:
        return response.results
    elif hasattr(response, "output") and response.output:
        return response.output
    elif hasattr(response, "content"):
        return response.content
    else:
        return response  # fallback
         
def run_agent(mcp_url: str,key: str, secret: str, serviceName: str, awsRegion: str):
    mcp_client = MCPClient(lambda: create_streamable_http_transport_sigv4(mcp_url,key,secret,serviceName, awsRegion))

    with mcp_client:
        tools = get_full_tools_list(mcp_client)
        print(f"Found the following tools: {[tool.tool_name for tool in tools]}")
        print(f"Tool name: {tools[0].tool_name}")
        
        
        agent = Agent(model=yourmodel,tools=tools) ## you can replace with any model you like
        print(f"Tools loaded in the agent are {agent.tool_names}")
        agent("notify ")
        #call mcp with tool
        tool=tools[0].tool_name
        tool_id="get-order-id-123-call-1"
        result = call_tool_sync(
            mcp_client,
            tool_id,
            tool_name=tool,
            parameters={"alarm": "instance id i-12345678 has CPU utilization over 90%", "message": "instance id i-12345678 has CPU utilization over 90% now!"}
        )

        print(f"Tool Call result: {result['content'][0]['text']}")

access=os.getenv('AWS_ACCESS_KEY_ID')
secret=os.getenv('AWS_SECRET_ACCESS_KEY')

# Run Agent with the credentials from this new gateway-invoke-role
run_agent("https://aiops-notification-gateway-e5rzuhdfca.gateway.bedrock-agentcore.ap-southeast-1.amazonaws.com/mcp",access,secret, SERVICE, os.environ['AWS_DEFAULT_REGION'])