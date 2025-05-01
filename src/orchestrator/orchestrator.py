from typing import List, Dict, Any, Optional, Callable
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
class Step:
    name: str
    tools: List[str]  # Simplified to just tool names
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
        self.processors: Dict[str, Dict[str, Callable]] = {}

    def _load_available_tools(self) -> List[str]:
        """Load available tools from the tools file"""
        tools_file = Path(__file__).parent.parent.parent / 'assets' / 'available.tools'
        tools = []
        
        with open(tools_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            tools = [row[0] for row in reader]
        
        return tools

    def register_processor(self, tool_name: str, input_proc: Optional[Callable] = None, 
                         output_proc: Optional[Callable] = None) -> None:
        """Register input/output processors for a specific tool"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Cannot register processors for unavailable tool: {tool_name}")
        
        self.processors[tool_name] = {
            "input": input_proc,
            "output": output_proc
        }

    def add_step(self, 
                 name: str, 
                 tools: List[str],  # Simplified to just tool names
                 depends_on: Optional[List[str]] = None,
                 initial_context: Dict[str, Any] = None) -> None:
        """Add a new step with multiple tools"""
        valid_tools = [tool for tool in tools if tool in self.available_tools]
        
        if not valid_tools:
            print(f"Warning: No valid tools found for step '{name}' - step will be skipped")
            return

        self.steps[name] = Step(
            name=name,
            tools=valid_tools,
            depends_on=depends_on,
            context=initial_context or {}
        )

    async def process_tool(self, tool_name: str, data: Any) -> Any:
        """Process tool execution with registered processors"""
        processors = self.processors.get(tool_name, {})
        
        # Apply input processor if registered
        if processors.get("input"):
            data = processors["input"](data)
            
        # Execute tool
        result = await self.mcp_client.execute_tool(tool_name, data)
        
        # Apply output processor if registered
        if processors.get("output"):
            result = processors["output"](result)
            
        return result

    async def execute_step(self, step: Step) -> Dict[str, Any]:
        """Execute a step's tools with processing"""
        step.status = StepStatus.RUNNING
        results = {}
        
        try:
            for tool_name in step.tools:
                result = await self.process_tool(tool_name, step.context)
                results[tool_name] = result
                # Update step context with tool result
                step.context[f"{tool_name}_result"] = result
            
            step.result = results
            step.status = StepStatus.COMPLETED
            return results
            
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