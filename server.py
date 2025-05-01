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
async def orchestrate_analysis(text: str) -> Dict[str, Any]:
    """Orchestrate a multi-step analysis process"""
    orchestrator = ProcessOrchestrator(mcp)
    
    # Configure step 1
    orchestrator.add_step(
        name="initial_analysis",
        tools=[
            {
                "name": "vibe_check",
                "input_processor": "prepare_vibe_input",
                "output_processor": "process_vibe_result"
            },
            {
                "name": "resolve-library-id",
                "input_processor": "prepare_library_input"
            },
            {
                "name": "sequentialthinking_tools"
            }
        ],
        initial_context={"input_text": text}
    )

    # Configure step 2
    orchestrator.add_step(
        name="deep_analysis",
        tools=[
            {
                "name": "vibe_learn",
                "input_processor": "prepare_vibe_learn_input"
            },
            {
                "name": "get-library-docs"
            },
            {
                "name": "sequentialthinking_tools"
            }
        ],
        depends_on=["initial_analysis"]
    )

    # Execute the process
    results = await orchestrator.execute()
    return results