from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("Example")

# Example sequential thinking configuration
sequential_config = {
    "goal": "Get and process resources",
    "thoughts": [
        {
            "tool": "get_resource_list",
            "input": {}
        },
        {
            "tool": "process_resources",
            "input": {
                "resources": "${previous.response}"
            }
        }
    ]
}

# Execute the sequential thinking
async def run_example():
    result = await mcp.execute_tool("sequential-thinking", sequential_config)
    print(f"Execution result: {result}")

# Run the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_example())