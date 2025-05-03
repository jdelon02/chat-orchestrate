from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import csv
import logging

# Set up logging configuration
log_file = Path(__file__).parent.parent.parent / 'mcp_tool_execution.log'
logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ProcessOrchestrator')

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Step:
    name: str
    tools: List[str]  # Simplified to just tool names
    status: StepStatus = StepStatus.PENDING
    result: Dict[str, Any] = None
    depends_on: Optional[List[str]] = None
    context: Dict[str, Any] = None

class ProcessOrchestrator:
    def __init__(self, mcp_client):
        """Initialize ProcessOrchestrator with FastMCP client"""
        self.mcp = mcp_client
        logger.info("ProcessOrchestrator initialized")
        # Log available methods on MCP client
        logger.info("MCP Client Methods:")
        for method_name in dir(self.mcp):
            if not method_name.startswith('_'):
                method = getattr(self.mcp, method_name)
                logger.info(f"- {method_name}: {method}")

    async def execute_chain(self, initial_input: str) -> Dict[str, Any]:
        """Execute a chain of tools, passing results through the sequence."""
        try:
            # First tool: run_context7 to get documentation
            logger.info(f"Starting documentation lookup for: {initial_input}")
            docs_result = await self.mcp.tool("run_context7")({
                "text": initial_input
            })
            logger.info("Documentation lookup completed")
            logger.debug(f"Documentation result: {docs_result}")

            # Check if we got valid documentation content
            if not docs_result.get("content"):
                logger.warning("No documentation content found")
                return docs_result

            # Second tool: vibe_check on the documentation content
            content_text = " ".join(docs_result["content"])
            logger.info("Starting sentiment analysis on documentation")
            logger.debug(f"Sentiment analysis input: {content_text[:100]}...")  # First 100 chars
            
            sentiment_result = await self.mcp.tool("vibe_check")({
                "userRequest": content_text
            })
            logger.info("Sentiment analysis completed")
            logger.debug(f"Sentiment result: {sentiment_result}")

            # Add sentiment analysis to the result
            docs_result["sentiment"] = sentiment_result
            logger.info("Chain execution completed successfully")
            
            return docs_result

        except Exception as e:
            logger.error(f"Error in execute_chain: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "isError": True
            }