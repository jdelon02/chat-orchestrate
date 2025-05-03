from fastmcp import FastMCP

# Example of using all three tool chains in one orchestration
async def run_unified_analysis(text: str = "Example text", library_query: str = "express middleware"):
    mcp = FastMCP("UnifiedExample")
    
    # Configure the chain with all three tool sets
    chain_config = {
        "steps": [
            {
                "name": "vibe_analysis",
                "tools": ["vibe_check", "vibe_learn", "vibe_distill"],
                "depends_on": []
            },
            {
                "name": "context_search",
                "tools": ["resolve-library-id", "get-library-docs"],
                "depends_on": ["vibe_analysis"]
            },
            {
                "name": "sequential_process",
                "tools": ["sequentialthinking_tools"],
                "depends_on": ["context_search"]
            }
        ],
        "initial_context": {
            "text": text,
            "library_query": library_query
        }
    }
    
    result = await mcp.execute_tool("orchestrate_chain", chain_config)
    return result

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_unified_analysis())
    print(result)