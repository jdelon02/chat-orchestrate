from fastmcp import FastMCP
from typing import Dict, Any

class VibeCheckClient:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.client_name = "vibe_check"

    async def execute(self, text: str) -> Dict[str, Any]:
        """Execute sentiment analysis using the vibe-check MCP tool"""
        result = await self.mcp("vibe-check", {
            "text": text
        })
        return {"sentiment": result}

async def vibe_check(text: str, mcp: FastMCP) -> Dict[str, Any]:
    """Convenience function to run vibe check without instantiating the class"""
    client = VibeCheckClient(mcp)
    return await client.execute(text)