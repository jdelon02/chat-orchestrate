from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import csv

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ToolConfig:
    name: str
    input_processor: Optional[str] = None
    output_processor: Optional[str] = None

@dataclass
class Step:
    name: str
    tools: List[ToolConfig]
    status: StepStatus = StepStatus.PENDING
    result: Dict[str, Any] = None
    depends_on: Optional[List[str]] = None
    context: Dict[str, Any] = None

class ProcessOrchestrator:
    def __init__(self, mcp_client):
        self.steps: Dict[str, Step] = {}
        self.available_tools: List[str] = self._load_available_tools()
        self.mcp_client = mcp_client
        self.global_context: Dict[str, Any] = {}

    def _load_available_tools(self) -> List[str]:
        """Load available tools from the tools file"""
        tools_file = Path(__file__).parent.parent.parent / 'assets' / 'available.tools'
        tools = []
        
        with open(tools_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            tools = [row[0] for row in reader]
        
        return tools

    def add_step(self, 
                 name: str, 
                 tools: List[Dict[str, Any]], 
                 depends_on: Optional[List[str]] = None,
                 initial_context: Dict[str, Any] = None) -> None:
        """
        Add a new step with multiple tools and their processors
        
        tools format: [
            {
                "name": "tool_name",
                "input_processor": "optional_function_name",
                "output_processor": "optional_function_name"
            }
        ]
        """
        tool_configs = []
        for tool in tools:
            if tool["name"] not in self.available_tools:
                raise ValueError(f"Tool {tool['name']} not available")
            tool_configs.append(ToolConfig(**tool))

        self.steps[name] = Step(
            name=name,
            tools=tool_configs,
            depends_on=depends_on,
            context=initial_context or {}
        )

    async def execute_step(self, step: Step) -> Dict[str, Any]:
        step.status = StepStatus.RUNNING
        try:
            # Update context with previous results if they exist
            if step.context:
                await self.mcp_client.update_context("previous_step_result", step.context)

            # Execute tool with context
            result = await self.mcp_client.execute_tool(
                step.tool,
                context=self.mcp_client.session_context
            )

            # Store result in context for next step
            await self.mcp_client.update_context(f"step_{step.name}_result", result)
            
            return result
        except Exception as e:
            step.status = StepStatus.FAILED
            raise RuntimeError(f"Step {step.name} failed: {str(e)}")

    async def execute(self) -> Dict[str, Any]:
        """Execute all valid steps in the orchestration process"""
        results = {}
        completed_steps = set()

        while len(completed_steps) < len(self.steps):
            for step_name, step in self.steps.items():
                if step_name in completed_steps:
                    continue

                # Skip if dependencies aren't met
                if step.depends_on and not all(dep in completed_steps for dep in step.depends_on):
                    continue

                # Skip empty steps
                if not step.tools:
                    print(f"Skipping empty step '{step_name}'")
                    completed_steps.add(step_name)
                    continue

                try:
                    results[step_name] = await self.execute_step(step)
                    completed_steps.add(step_name)
                except Exception as e:
                    print(f"Error executing step '{step_name}': {str(e)}")
                    step.status = StepStatus.FAILED
                    raise

        return results