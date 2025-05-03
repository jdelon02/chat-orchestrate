from fastmcp import FastMCP
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Context7Client:
    def __init__(self, mcp: FastMCP = None, query: str = ""):
        """Initialize Context7Client"""
        self.client_name = "context7"
        self.mcp = mcp
        self.query = query
        self.context = {}
        # Single step using run_context7 which combines both tools
        self.steps = {
            "get_documentation": {
                "tool": "run_context7",
                "depends_on": [],
                "context": {}
            }
        }
    
    def get_step_input(self, step_name: str) -> Dict[str, Any]:
        """Return appropriate input data for the step"""
        if step_name == "get_documentation":
            return {
                "text": self.query
            }
        return {}

    def update_context(self, step_name: str, result: Any) -> None:
        """Update context based on step results"""
        self.context[step_name] = result

    def get_final_result(self) -> Dict[str, Any]:
        """Format final result to match server implementation"""
        result = self.context.get("get_documentation", {})
        return result

    async def execute(self, query: str = None) -> Dict[str, Any]:
        """Execute Context7 analysis using run_context7 tool"""
        if query:
            self.query = query
        
        try:
            # Use MCP client directly instead of SSE manager
            result = await self.mcp.call_tool("run_context7")({
                self.query
            })
            return result
        except Exception as e:
            logger.error(f"Error executing Context7 analysis: {str(e)}")
            return {"error": str(e), "isError": True}

async def run_context7(query: str, mcp: FastMCP) -> Dict[str, Any]:
    """Convenience function to run Context7 without instantiating the class"""
    client = Context7Client(mcp=mcp, query=query)
    return await client.execute()