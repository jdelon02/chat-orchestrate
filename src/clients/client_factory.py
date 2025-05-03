from typing import Dict, Any, Optional
from .vibe_check import VibeCheckClient
from .context7 import Context7Client
from .sequential_thinking import SequentialThinkingClient

class ClientFactory:
    @staticmethod
    def create_client(client_type: str, **kwargs) -> Optional[Any]:
        """Create and return appropriate client based on type"""
        clients = {
            'vibe': VibeCheckClient,
            'context7': Context7Client,
            'sequential': SequentialThinkingClient
        }
        
        client_class = clients.get(client_type.lower())
        if client_class:
            return client_class(**kwargs)
        return None

    @staticmethod
    def get_client_steps(client: Any) -> Dict[str, Dict[str, Any]]:
        """Get steps configuration from client"""
        return getattr(client, 'steps', {})