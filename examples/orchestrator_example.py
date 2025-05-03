import asyncio
from fastmcp import FastMCP
from src.orchestrator.orchestrator import ProcessOrchestrator
import logging
from pathlib import Path

# Set up logging configuration
log_file = Path(__file__).parent.parent / 'mcp_tool_execution.log'
logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting orchestrator example")
        # Initialize FastMCP client
        mcp = FastMCP("ChainExample")
        logger.info("FastMCP client initialized")
        
        # Create orchestrator
        orchestrator = ProcessOrchestrator(mcp)
        logger.info("ProcessOrchestrator created")
        
        # Execute the chain
        logger.info("Executing chain with query: How do I use Python's asyncio library?")
        result = await orchestrator.execute_chain(
            "How do I use Python's asyncio library?"
        )
        
        # Check for errors
        if result.get("isError"):
            logger.error(f"Chain execution failed: {result.get('error')}")
            return
        
        # Log and print results
        logger.info("Chain execution completed successfully")
        print("\nDocumentation:")
        for content in result.get("content", []):
            print("-" * 40)
            print(content)
            logger.debug(f"Documentation content: {content[:100]}...")  # Log first 100 chars
        
        print("\nSentiment Analysis:")
        sentiment = result.get("sentiment")
        print(sentiment)
        logger.info(f"Sentiment analysis result: {sentiment}")
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())