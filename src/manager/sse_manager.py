import base64
import asyncio
from fastmcp import Client
from fastmcp.client.transports import SSETransport
from typing import AsyncGenerator, Dict, Any
from datetime import datetime


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
        await self.connect()
        return await self._client.list_tools()

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