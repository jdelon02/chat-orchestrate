import base64
from fastmcp import Client, Context
from fastmcp.client.transports import SSETransport
from typing import Optional, AsyncGenerator, Dict, Any
from datetime import datetime


class SSEClientManager:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.headers = self._create_headers()
        self.session_context: Dict[str, Any] = {}
        self.session_start = datetime.now()

    def _create_headers(self) -> dict:
        """Create headers with Basic Auth and SSE requirements"""
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()

        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }

    async def get_resources(self) -> AsyncGenerator[dict, None]:
        """Get resources from SSE server"""
        transport = SSETransport(self.base_url, headers=self.headers)
        async with Client(transport) as client:
            resources = await client.list_resources()
            for resource in resources:
                if isinstance(resource, dict):
                    resource_id = resource.get('id', '')
                    yield {
                        'event': 'resource',
                        'data': {
                            'name': resource.get('name', ''),
                            'description': resource.get('description', ''),
                            'type': resource.get('type', ''),
                            'status': resource.get('status', '')
                        },
                        'id': resource_id,
                        'retry': 1000
                    }

    async def update_context(self, key: str, value: Any) -> None:
        """Update the session context with new information"""
        self.session_context[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }

    async def get_context(self, key: str) -> Optional[Any]:
        """Retrieve value from session context"""
        if key in self.session_context:
            return self.session_context[key]['value']
        return None

    async def get_tools(self) -> dict:
        """Get tools from SSE server with context"""
        transport = SSETransport(self.base_url, headers=self.headers)
        async with Client(transport) as client:
            # Create a context object for this request
            context = Context()
            context.set("session_start", self.session_start.isoformat())
            context.set("session_context", self.session_context)
            
            # Pass context to the client call
            return await client.list_tools(context=context)