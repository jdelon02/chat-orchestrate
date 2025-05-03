from fastmcp import FastMCP
from typing import List

class SequentialThinkingClient:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.client_name = "sequential_thinking"

    async def execute(self, problem: str, steps: List[str]) -> dict:
        """Execute sequential problem solving analysis"""
        steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        result = await self.mcp.execute_tool(
            "chat",
            {
                "messages": [
                    {"role": "system", "content": "You are an expert at breaking down and solving problems step by step."},
                    {"role": "user", "content": f"Problem: {problem}\n\nAnalyze this problem following these steps:\n{steps_str}"}
                ]
            }
        )
        return {"analysis": result}

async def run_sequential_thinking(problem: str, steps: List[str], mcp: FastMCP) -> dict:
    """Convenience function to run sequential thinking without instantiating the class"""
    client = SequentialThinkingClient(mcp)
    return await client.execute(problem, steps)