import base64
import asyncio
import logging
import inspect
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import SSETransport
from typing import AsyncGenerator, Dict, Any
from datetime import datetime

# Set up logging configuration
log_file = Path(__file__).parent.parent.parent / 'mcp_tool_execution.log'
logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SSEClientManager')


class SSEClientManager:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = self._create_headers()
        self._client = None
        self._transport = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Establish connection with SSE server"""
        if not self._transport:
            self._transport = SSETransport(
                self.base_url,
                headers=self.headers
            )
        if not self._client:
            self._client = Client(self._transport)
            await self._client.__aenter__()

    async def disconnect(self):
        """Close connection with SSE server"""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
            self._transport = None

    def _create_headers(self) -> dict:
        """Create headers with Basic Auth and SSE requirements"""
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()

        return {
            "Authorization": f"Basic {credentials}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }

    async def get_tools(self) -> Dict[str, Any]:
        """Get tools from SSE server"""
        try:
            logger.info("Fetching available tools from SSE server")
            start_time = datetime.now()
            
            await self.connect()
            tools = await self._client.list_tools()
            
            execution_time = datetime.now() - start_time
            logger.info(f"Tools fetched successfully in: {execution_time}")
            
            # Simple string output of tools
            logger.info("-" * 50)
            logger.info("Available Tools:")
            logger.info(f"{tools}")
            logger.info("-" * 50)
            
            return tools
            
        except Exception as e:
            logger.error(f"Error fetching tools: {str(e)}")
            raise

    async def get_resources(self) -> AsyncGenerator[dict, None]:
        """Get resources from SSE server using FastMCP's list_resources method"""
        await self.connect()
        resources = await self._client.list_resources()
        for resource in resources:
            if isinstance(resource, dict):
                yield {
                    'event': 'resource',
                    'data': resource,
                    'retry': 1000
                }

    def _inspect_client(self) -> Dict[str, Any]:
        """Inspect the FastMCP Client class structure and methods"""
        client_info = {
            "class_name": self._client.__class__.__name__,
            "module": self._client.__class__.__module__,
            "mro": [cls.__name__ for cls in self._client.__class__.__mro__],
            "methods": {},
            "attributes": {},
            "callable_status": callable(self._client),
        }

        # Get all methods
        for name, member in inspect.getmembers(self._client.__class__):
            if inspect.isfunction(member) or inspect.ismethod(member):
                client_info["methods"][name] = {
                    "signature": str(inspect.signature(member)),
                    "doc": inspect.getdoc(member),
                    "source": inspect.getsource(member) if not name.startswith('__') else "Built-in method"
                }

        # Get all attributes
        for name in dir(self._client):
            if not name.startswith('_'):  # Skip private attributes
                try:
                    attr = getattr(self._client, name)
                    client_info["attributes"][name] = {
                        "type": type(attr).__name__,
                        "repr": repr(attr) if not callable(attr) else "Callable"
                    }
                except Exception as e:
                    client_info["attributes"][name] = f"Error accessing: {str(e)}"

        return client_info

    async def execute_tool(self, tool_name: str, data: Dict[str, Any]) -> Any:
        """Execute a specific tool through the SSE connection
        
        Args:
            tool_name: Name of the tool to execute
            data: Data to pass to the tool
            
        Returns:
            Tool execution results
        """
        await self.connect()
        
        try:
            # Keep existing debug logging
            logger.info("Client Structure Information:")
            client_info = self._inspect_client()
            for section, content in client_info.items():
                logger.info(f"\n{section.upper()}:")
                logger.info(f"{content}")

            # Convert tool name from kebab-case to snake_case
            # tool_name = tool_name.replace("-", "_")
            
            # Log tool execution details
            logger.info(f"Executing tool: {tool_name}")
            logger.info(f"Input data: {data}")
            start_time = datetime.now()
            
            result = await self._client.call_tool(tool_name, data)
            
            execution_time = datetime.now() - start_time
            logger.info(f"Tool execution completed in: {execution_time}")
            logger.info("Tool Execution Result:")
            logger.info("-" * 50)
            logger.info(f"Result Type: {type(result).__name__}")
            logger.info(f"Raw Result: {result}")
            if isinstance(result, (list, dict)):
                logger.info(f"Result Structure: {result}")
            logger.info("-" * 50)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            logger.error(f"Input data was: {data}")
            logger.error("-" * 50)
            raise