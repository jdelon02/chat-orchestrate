from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Context7Context:
    """Context object to maintain state between Context7 tool calls"""
    query: str
    library_id: Optional[str] = None
    library_docs: Optional[Dict] = None

class Context7Client:
    def __init__(self, query: str):
        self.context = Context7Context(query=query)
        self.steps = {
            "resolve": {
                "tool": "resolve-library-id",
                "depends_on": None
            },
            "fetch_docs": {
                "tool": "get-library-docs",
                "depends_on": ["resolve"]
            }
        }

    def get_step_input(self, step_name: str) -> Dict[str, Any]:
        """Prepare input for each Context7 step based on context"""
        if step_name == "resolve":
            return {"query": self.context.query}
        elif step_name == "fetch_docs":
            return {
                "query": self.context.query,
                "library_id": self.context.library_id
            }
        raise ValueError(f"Unknown step: {step_name}")

    def update_context(self, step_name: str, result: Any) -> None:
        """Update context with step results"""
        if step_name == "resolve":
            self.context.library_id = result.get('library_id')
        elif step_name == "fetch_docs":
            self.context.library_docs = result

    def get_final_result(self) -> Dict[str, Any]:
        """Return the final processed result"""
        return {
            "query": self.context.query,
            "library_id": self.context.library_id,
            "library_docs": self.context.library_docs
        }