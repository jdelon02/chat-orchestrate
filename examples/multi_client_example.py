from fastmcp import FastMCP
from src.orchestrator.orchestrator import ProcessOrchestrator

async def run_multi_client_example():
    mcp = FastMCP("MultiClientExample")
    orchestrator = ProcessOrchestrator(mcp)
    
    # Context7 example for library search
    orchestrator.set_specialized_client('context7', query="express middleware")
    context7_result = await orchestrator.execute()
    print("Context7 Result:", context7_result)
    
    # Vibe check example for sentiment analysis
    orchestrator.set_specialized_client('vibe_check', text="I love working with this amazing framework!")
    vibe_check_result = await orchestrator.execute()
    print("Vibe Check Result:", vibe_check_result)
    
    # Sequential thinking example for problem solving
    orchestrator.set_specialized_client('sequential_thinking', 
        problem="How to implement a caching system for a web application",
        steps=["Identify requirements", "Choose cache storage", "Implement cache logic", "Add error handling"])
    sequential_result = await orchestrator.execute()
    print("Sequential Thinking Result:", sequential_result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_multi_client_example())