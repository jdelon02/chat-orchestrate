from fastmcp import FastMCP
from src.clients.context7 import Context7Client, run_context7_search

async def main(query: str = "express middleware"):
    mcp = FastMCP("Context7Example")
    
    # Method 1: Using the client class
    client = Context7Client(mcp)
    result1 = await client.execute(query)
    print("Using client class:", result1)
    
    # Method 2: Using the convenience function
    result2 = await run_context7_search(query, mcp)
    print("Using convenience function:", result2)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())