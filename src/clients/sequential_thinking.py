from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class SequentialContext:
    """Context object for sequential thinking process"""
    initial_query: str
    thought_steps: List[str] = None
    final_analysis: Optional[Dict] = None

class SequentialThinkingClient:
    def __init__(self, query: str):
        self.context = SequentialContext(
            initial_query=query,
            thought_steps=[]
        )
        self.steps = {
            "analyze": {
                "tool": "sequentialthinking_tools",
                "depends_on": None
            }
        }

    def get_step_input(self, step_name: str) -> Dict[str, Any]:
        """Prepare input for sequential thinking tool"""
        if step_name == "analyze":
            return {
                "query": self.context.initial_query,
                "previous_steps": self.context.thought_steps
            }
        raise ValueError(f"Unknown step: {step_name}")

    def update_context(self, step_name: str, result: Any) -> None:
        """Update context with step results"""
        if step_name == "analyze":
            if isinstance(result, dict):
                self.context.thought_steps = result.get('steps', [])
                self.context.final_analysis = result.get('analysis')

    def get_final_result(self) -> Dict[str, Any]:
        """Return the final processed result"""
        return {
            "query": self.context.initial_query,
            "thought_steps": self.context.thought_steps,
            "analysis": self.context.final_analysis
        }