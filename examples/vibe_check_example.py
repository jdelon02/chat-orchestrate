from fastmcp import FastMCP
from src.clients.vibe_check import VibeCheckClient

async def main(text: str = "I love working with this amazing framework!"):
    mcp = FastMCP("VibeCheckExample")
    client = VibeCheckClient(mcp)
    result = await client.execute(text)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())