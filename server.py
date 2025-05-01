# server.py
import httpx
from fastmcp import Context, FastMCP, Client
from sse_starlette.sse import EventSourceResponse
from src.utils.processor import ProcessorClass
from src.manager.sse_manager import SSEClientManager
from typing import Dict, Any
from src.orchestrator.orchestrator import ProcessOrchestrator  # Fixed import path


# Create an MCP server
mcp = FastMCP("Demo")

# Initialize SSE client manager
sse_manager = SSEClientManager(
    base_url="http://192.168.86.67:3000/sse",
    username="admin",
    password="Thin1buoy2"
)

processor = ProcessorClass()


@mcp.tool()
async def get_tool_list() -> str:
    """Connect to SSE server and return results"""
    tools = await sse_manager.get_tools()
    try:
        # Process the tools data
        await processor.process_tools(tools)
    except Exception as e:
        print(f"Error processing tools data: {str(e)}")
        raise
    return tools
   
@mcp.resource("resources://list")
async def get_resource_list() -> EventSourceResponse:
    """Get a list of resources from the SSE server and return as streaming events"""
    # Get the generator without calling it
    event_generator = sse_manager.get_resources()
    # Pass the generator directly to EventSourceResponse
    return EventSourceResponse(event_generator)

@mcp.tool()
async def orchestrate_chain(chain_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a configured chain of tools
    
    Expected config format:
    {
        "initial_context": {
            "query": "user query here",
            "other_params": "other values"
        },
        "steps": [
            {
                "name": "initial_analysis",
                "tools": ["vibe_check", "sequentialthinking_tools"],
                "depends_on": None
            },
            {
                "name": "library_check",
                "tools": ["resolve-library-id", "get-library-docs"],
                "depends_on": ["initial_analysis"]
            }
        ]
    }
    """
    orchestrator = ProcessOrchestrator(mcp)
    
    # Configure steps from chain config
    for step in chain_config["steps"]:
        orchestrator.add_step(
            name=step["name"],
            tools=step["tools"],
            depends_on=step["depends_on"],
            initial_context=chain_config.get("initial_context", {})
        )

    # Execute the configured chain
    results = await orchestrator.execute()
    return results