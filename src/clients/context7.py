from fastmcp import FastMCP

class Context7Client:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.client_name = "context7"

    async def execute(self, query: str) -> dict:
        """Execute library search"""
        result = await self.mcp.execute_tool(
            "chat",
            {
                "messages": [
                    {"role": "system", "content": "You are a library search expert."},
                    {"role": "user", "content": f"Search for relevant libraries and documentation for: {query}"}
                ]
            }
        )
        return {"search_results": result}

async def run_context7_search(query: str, mcp: FastMCP) -> dict:
    """Convenience function to run context7 search without instantiating the class"""
    client = Context7Client(mcp)
    return await client.execute(query)