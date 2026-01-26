# mcp/mcp_server.py
import sys
import os
import requests

# Redirect stdout to avoid breaking JSON-RPC protocol
sys.stdout = sys.stderr

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TNGD_Actions")

@mcp.tool()
def fetch_balance(query: str) -> str:
    """
    This is a MCP tool to fetch user current ewallet balance. 
    Use this for questions about: balance, wallet amount,
    """
    return "RM 1,250.00 [MCP Response]"

@mcp.tool()
def sys_status(query: str) -> str:
    """
    This is a MCP tool to check the real-time operational status of TNGD digital services. 
    Use this for questions about: system down, server error, maintenance, 
    is TNG working, or service availability.
    """
    return "All Systems Operational [MCP Response]"

#----------------------------
# Calling workflow from Dify

DIFY_API_KEY = "app-YmFSDwnjPnkByd2NzRjNMWec"
DIFY_WORKFLOW_URL = "https://api.dify.ai/v1/workflows/run"

@mcp.tool()
def ask_dify(query: str) -> str:
    """
    This is a MCP tool to check the platform and backend only
    """
    #----------------------------
    print (f"KY-DEBUG Executing Dify workflow for query: {query}")
    import logging
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logging.info(f"KY-DEBUG Executing Dify workflow for query: {query}")
    #----------------------------

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Workflow Request Body
    # Note: 'inputs' must contain at least one key/value pair based on your Dify node setup.
    # If your Dify Start Node variable is named 'user_query', change "{'query': query}" accordingly.
    payload = {
        "inputs": {"query": query}, 
        "response_mode": "blocking",
        "user": "mcp_client_user"
    }

    try:
        response = requests.post(DIFY_WORKFLOW_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        outputs = result.get("data", {}).get("outputs", {})
        
        if outputs:
            return str(outputs)

        return "Dify workflow executed but returned no text output. [MCP Status]"

    except requests.exceptions.HTTPError as err:
        return f"Dify API Error: {err.response.text}"
    except Exception as e:
        return f"Error connecting to Dify: {str(e)}"
    
#----------------------------

if __name__ == "__main__":
    # Ensure this matches the port in your app.py (http://localhost:8000/sse)
    mcp.run(transport="sse")