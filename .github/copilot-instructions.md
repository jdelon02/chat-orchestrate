# Copilot Instructions for MCP Orchestrator

This project is built on top of the FastMCP framework and implements its patterns and conventions. The primary goal is to provide a single orchestration tool that can execute multiple remote MCP tools in a coordinated manner. Users should be able to invoke one tool that then manages and executes multiple defined remote MCP tools based on the orchestration logic.

This project is a Python-based orchestration tool for managing and executing multiple tools in a coordinated manner, using FastMCP and async/await patterns.

## Project Structure
- `src/clients/`: Individual tool clients (VibeCheck, Context7, SequentialThinking)
- `src/manager/`: SSE management functionality
- `src/orchestrator/`: Core orchestration logic
- `src/utils/`: Utility functions and helpers
- `examples/`: Example implementations
- `assets/`: Runtime assets (e.g., available tools list)

## Framework Alignment
- Follow FastMCP patterns for tool implementation
- Use FastMCP's async client patterns for tool integration
- Implement FastMCP's event handling and SSE management approaches
- Maintain compatibility with FastMCP's versioning and interfaces
- Use FastMCP's recommended error handling patterns

## Design Goals
- Provide a single entry point for executing multiple MCP tools
- Handle tool dependencies and execution order
- Manage state and context across multiple tool executions
- Abstract away the complexity of individual tool interactions
- Support configurable tool chains and execution patterns

## Coding Standards
- Use Python 3.10 or higher
- Use async/await for asynchronous operations
- Use 4 spaces for indentation
- Use type hints and docstrings
- Follow PEP 8 naming conventions:
  - snake_case for functions and variables
  - PascalCase for classes
  - UPPER_CASE for constants
- Use dataclasses for data structures where appropriate

## Project Patterns
- Client implementation follows factory pattern
- Orchestrator uses step-based execution with dependencies
- Use dependency injection for MCP client
- Implement async context managers with __aenter__ and __aexit__
- Use type hints for better code clarity

## Key Components
- ProcessOrchestrator: Main orchestration class
- SSEClientManager: Manages SSE connections
- ClientFactory: Creates specialized clients
- VibeCheckClient/Context7Client/SequentialThinkingClient: Specialized tool clients

## Common Imports
```python
from fastmcp import FastMCP, Client
from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import httpx
from dataclasses import dataclass
```

## Error Handling
- Use specific exception types
- Implement proper async cleanup in context managers
- Propagate errors with meaningful context
- Use try/except blocks for recoverable errors

## Tool Configuration
- Context7 libraries are configured in .vscode/settings.json
- Libraries specified in context7.libraries setting are loaded automatically
- Project root is set to workspace folder
- Modify .vscode/settings.json to update Context7 library references