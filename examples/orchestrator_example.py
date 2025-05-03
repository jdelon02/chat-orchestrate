import asyncio
from fastmcp import FastMCP
from src.orchestrator.process_orchestrator import ProcessOrchestrator
from src.clients.context7_client import Context7Client
from src.clients.vibecheck_client import VibeCheckClient

async def main():
    # Initialize FastMCP client
    mcp = FastMCP()
    
    # Create orchestrator instance
    orchestrator = ProcessOrchestrator(mcp)
    
    # Define a sample workflow
    workflow = {
        "tools": [
            {
                "name": "context7",
                "input": "Please analyze this code with the configured libraries.",
                "code": "your_code_here"
            },
            {
                "name": "vibecheck",
                "input": "Check the style and patterns of this code.",
                "code": "your_code_here"
            }
        ]
    }
    
    # Execute the workflow
    async for result in orchestrator.execute(workflow):
        print(f"Result from {result['tool']}: {result['response']}")

if __name__ == "__main__":
    asyncio.run(main())