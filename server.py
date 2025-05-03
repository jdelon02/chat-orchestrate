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
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
async def run_context7(data: Dict[str, str]) -> Dict[str, Any]:
    logger.info("Starting run_context7 with input: %s", data)
    async with await get_sse_manager() as manager:
        text = data["text"]
        logger.debug("Resolving library ID for text: %s", text)
        
        try:
            # First get library ID
            response = await manager.execute_tool(
                "resolve-library-id",
                {   
                    "libraryName": text
                }
            )
            
            # Extract text from TextContent object
            if isinstance(response, list) and len(response) > 0:
                library_text = response[0].text if hasattr(response[0], 'text') else str(response[0])
                
                # Try to find the library ID in the text
                if "Context7-compatible library ID:" in library_text:
                    library_id = library_text.split("Context7-compatible library ID:")[1].split("\n")[0].strip()
                    logger.info("Found library ID: %s", library_id)
                    
                    # Get library docs and extract text content
                    library_docs = await manager.execute_tool(
                        "get-library-docs",
                        {
                            "context7CompatibleLibraryID": library_id
                        }
                    )
                    
                    # Convert TextContent objects to plain text
                    if isinstance(library_docs, list):
                        result = {
                            "content": [
                                doc.text if hasattr(doc, 'text') else str(doc)
                                for doc in library_docs
                            ],
                            "isError": False
                        }
                        logger.info("Successfully retrieved library docs")
                        return result
                    
            logger.warning("No valid library ID found in response")
            return {"error": "No valid library ID found in response"}
            
        except Exception as e:
            logger.error("Error executing resolve-library-id: %s", str(e))
            return {"error": f"Failed to resolve library ID: {str(e)}"}


@mcp.tool()
async def run_sequential_thinking(query: str) -> Dict[str, Any]:
    """Run a sequential thinking process"""
    client = SequentialThinkingClient(mcp)
    return await client.execute(query)

@mcp.tool()
async def orchestrate(data: Dict[str, str]) -> Dict[str, Any]:
    """
    Orchestrate multiple tools in sequence, passing results through the chain.
    Expects input with 'text' key containing the initial query.
    """
    logger.info("Starting orchestration with input: %s", data)
    async with await get_sse_manager() as manager:
        try:
            initial_text = data["text"]
            result = {}
            
            # Step 1: Get documentation using run_context7
            logger.info("Step 1: Getting documentation")
            docs_result = await run_context7({initial_text})
            
            if docs_result.get("isError"):
                logger.error("Documentation lookup failed: %s", docs_result.get("error"))
                return docs_result
                
            result.update(docs_result)
            
            # Step 2: Run sentiment analysis on the documentation
            if docs_result.get("content"):
                logger.info("Step 2: Running sentiment analysis")
                content_text = " ".join(docs_result["content"])
                sentiment_result = await run_vibe_check({
                    "text": content_text
                })
                
                # Add sentiment to result
                result["sentiment"] = sentiment_result.get("sentiment")
            
            logger.info("Orchestration completed successfully")
            
            # Return simplified result structure
            return {
                "documentation": docs_result.get("content", []),
                "sentiment": result.get("sentiment"),
                "isError": False
            }
            
        except Exception as e:
            logger.error("Error in orchestration: %s", str(e))
            return {
                "error": str(e),
                "isError": True
            }


