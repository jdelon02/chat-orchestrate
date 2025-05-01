from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class VibeContext:
    """Context object to maintain state between vibe tool calls"""
    initial_text: str
    check_result: Optional[Dict] = None
    learn_result: Optional[Dict] = None
    distill_result: Optional[Dict] = None

class VibeCheckClient:
    def __init__(self, initial_text: str):
        self.context = VibeContext(initial_text=initial_text)
        self.steps = {
            "check": {
                "tool": "vibe_check",
                "depends_on": None
            },
            "learn": {
                "tool": "vibe_learn",
                "depends_on": ["check"]
            },
            "distill": {
                "tool": "vibe_distill",
                "depends_on": ["learn"]
            }
        }

    def get_step_input(self, step_name: str) -> Dict[str, Any]:
        """Prepare input for each vibe step based on context"""
        if step_name == "check":
            return {"text": self.context.initial_text}
        elif step_name == "learn":
            return {
                "text": self.context.initial_text,
                "check_result": self.context.check_result
            }
        elif step_name == "distill":
            return {
                "text": self.context.initial_text,
                "check_result": self.context.check_result,
                "learn_result": self.context.learn_result
            }
        raise ValueError(f"Unknown step: {step_name}")

    def update_context(self, step_name: str, result: Any) -> None:
        """Update context with step results"""
        if step_name == "check":
            self.context.check_result = result
        elif step_name == "learn":
            self.context.learn_result = result
        elif step_name == "distill":
            self.context.distill_result = result

    def get_final_result(self) -> Dict[str, Any]:
        """Return the final processed result"""
        return {
            "final_result": self.context.distill_result,
            "full_context": self.context
        }