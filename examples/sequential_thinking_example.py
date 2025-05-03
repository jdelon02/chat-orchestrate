from fastmcp import FastMCP
from src.clients.sequential_thinking import SequentialThinkingClient, run_sequential_thinking

async def main(
    problem: str = "How to implement a caching system for a web application",
    steps: list = ["Identify requirements", "Choose cache storage", "Implement cache logic", "Add error handling"]
):
    mcp = FastMCP("SequentialThinkingExample")
    
    # Method 1: Using the client class
    client = SequentialThinkingClient(mcp)
    result1 = await client.execute(problem, steps)
    print("Using client class:", result1)
    
    # Method 2: Using the convenience function
    result2 = await run_sequential_thinking(problem, steps, mcp)
    print("Using convenience function:", result2)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())