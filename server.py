# server.py
import asyncio
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

async def get_sse_manager() -> SSEClientManager:
    """Get or create SSE manager instance"""
    return sse_manager


@mcp.tool()
async def get_tool_list() -> Dict[str, Any]:
    """Get available tools using FastMCP's built-in list_tools method"""
    try:
        async with await get_sse_manager() as manager:
            return await manager._client.list_tools()
    except Exception as e:
        if "timeout" in str(e).lower():
            return {
                "status": "error",
                "error": "Request timed out. Please try again."
            }
        return {
            "status": "error",
            "error": str(e)
        }
    
   
@mcp.resource("resources://list")
async def get_resource_list() -> EventSourceResponse:
    """Get a list of resources from the SSE server and return as streaming events"""
    async with await get_sse_manager() as manager:
        event_generator = manager.get_resources()
        return EventSourceResponse(event_generator)

@mcp.tool()
async def orchestrate_chain(chain_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a configured chain of tools
    """
    async with await get_sse_manager() as manager:
        orchestrator = ProcessOrchestrator(mcp)
        
        for step in chain_config["steps"]:
            orchestrator.add_step(
                name=step["name"],
                tools=step["tools"],
                depends_on=step["depends_on"],
                initial_context=chain_config.get("initial_context", {})
            )

        return await orchestrator.execute()