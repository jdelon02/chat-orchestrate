import asyncio
import logging
from fastmcp import FastMCP
from src.orchestrator.orchestrator import ProcessOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Example showing how to use the Context7Client with ProcessOrchestrator"""
    # Initialize FastMCP client with name
    mcp = FastMCP("Context7Example")
    
    # Create orchestrator instance with mcp client
    orchestrator = ProcessOrchestrator(mcp)
    
    # Initialize with query
    query = "How do I use Python's asyncio library?"
    
    # Set specialized client with mcp instance
    orchestrator.set_specialized_client('context7', mcp=mcp, query=query)
    
    try:
        # Execute the orchestration
        result = await orchestrator.execute()
        
        if not result.get("isError", True):
            # Process successful result
            logger.info("Successfully retrieved documentation:")
            for content in result.get("content", []):
                logger.info("---")
                logger.info(content)
        else:
            # Handle error case
            logger.error(f"Error retrieving documentation: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())