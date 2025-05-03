# server.py
import asyncio
import httpx
from fastmcp import Context, FastMCP, Client
from sse_starlette.sse import EventSourceResponse
from src.utils.processor import ProcessorClass
from src.manager.sse_manager import SSEClientManager
from typing import Dict, Any
from src.orchestrator.orchestrator import ProcessOrchestrator  # Fixed import path
from src.clients.vibe_check import VibeCheckClient
from src.clients.context7 import Context7Client
from src.clients.sequential_thinking import SequentialThinkingClient

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
    """Execute a configured chain of tools"""
    async with await get_sse_manager() as manager:
        orchestrator = ProcessOrchestrator(mcp)
        context = chain_config.get("initial_context", {})
        
        for step in chain_config["steps"]:
            # Determine which specialized client to use based on tools
            if "vibe_check" in step["tools"]:
                orchestrator.set_specialized_client('vibe', initial_text=context.get("text", ""))
            elif "resolve-library-id" in step["tools"]:
                orchestrator.set_specialized_client('context7', query=context.get("library_query", ""))
            elif "sequentialthinking_tools" in step["tools"]:
                orchestrator.set_specialized_client('sequential', query=str(context))

            orchestrator.add_step(
                name=step["name"],
                tools=step["tools"],
                depends_on=step["depends_on"],
                initial_context=context
            )

        result = await orchestrator.execute()
        # Update context with results for next steps
        context.update(result)
        return result

@mcp.tool()
async def run_vibe_check(data: Dict[str, str]) -> Dict[str, Any]:
    async with await get_sse_manager() as manager:
        text = data["text"]
        response = await manager.execute_tool(
            "vibe_check",
            {
                "userRequest": text  # Changed from "text" to "userRequest"
            }
        )
        return {"sentiment": response}

@mcp.tool()
async def run_context7_lookup(data: Dict[str, str]) -> Dict[str, Any]:
    async with await get_sse_manager() as manager:
        text = data["text"]
        response = await manager.execute_tool(
            "resolve-library-id",
            {   
                "libraryName": text  # Changed from "text" to "userRequest"
            }
        )
        return {"context7CompatibleLibraryID": response}
    
@mcp.tool()
async def run_context7_search(query: str) -> Dict[str, Any]:
    """Run a Context7 search process"""
    client = Context7Client(mcp)
    return await client.execute(query)

@mcp.tool()
async def run_sequential_thinking(query: str) -> Dict[str, Any]:
    """Run a sequential thinking process"""
    client = SequentialThinkingClient(mcp)
    return await client.execute(query)

async def _analyze_sentiment(text: str) -> str:
    """Internal function to analyze sentiment"""
    async with await get_sse_manager() as manager:
        response = await manager._client.chat([
            {"role": "system", "content": "You are a sentiment analysis expert."},
            {"role": "user", "content": f"Analyze the sentiment of this text: {text}"}
        ])
        return response