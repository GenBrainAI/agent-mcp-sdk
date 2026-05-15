"""AgentMCPServer — MCP server with built-in agent.ceo integration.

This module provides the core server class for building MCP servers
that integrate with the agent.ceo Cyborgenic Organization platform.

Usage:
    from agent_mcp import AgentMCPServer, tool

    server = AgentMCPServer(name="my-tools")

    @server.tool()
    async def my_tool(arg: str) -> dict:
        return {"result": arg}

    server.run()
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


def tool(name: str | None = None, description: str | None = None):
    """Decorator to register a function as an MCP tool.

    Can be used with or without arguments:

        @server.tool()
        async def my_tool(x: int) -> dict: ...

        @server.tool(name="custom-name", description="Override docstring")
        async def my_tool(x: int) -> dict: ...
    """

    def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        fn._mcp_tool = True
        fn._mcp_tool_name = name or fn.__name__
        fn._mcp_tool_description = description or fn.__doc__ or ""
        return fn

    return decorator


@dataclass
class ToolDefinition:
    """Internal representation of a registered MCP tool."""

    name: str
    description: str
    handler: Callable[..., Coroutine]
    parameters: dict[str, Any] = field(default_factory=dict)


class AgentCEOClient:
    """Client for interacting with the agent.ceo platform.

    Provides methods for task delegation, inbox management,
    knowledge base queries, and agent discovery within a
    Cyborgenic Organization.
    """

    def __init__(self, token: str | None = None, organization_id: str | None = None):
        self.token = token or os.getenv("AGENT_CEO_TOKEN", "")
        self.organization_id = organization_id or os.getenv("AGENT_CEO_ORG_ID", "")

    async def assign_task(self, role: str, description: str, priority: str = "medium") -> Any:
        """Assign a task to an agent by role."""
        # TODO: Implement agent.ceo API call
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")

    async def get_inbox(self, agent_id: str | None = None) -> list[Any]:
        """Retrieve inbox messages for an agent."""
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")

    async def wiki_search(self, query: str, limit: int = 5) -> list[Any]:
        """Search the organization knowledge base."""
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")

    async def wiki_get_page(self, path: str) -> Any:
        """Retrieve a wiki page by path."""
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")

    async def discover_agents(self) -> list[Any]:
        """List all agents in the current organization."""
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")

    async def send_message(self, to: str, subject: str, body: str) -> Any:
        """Send a message to another agent."""
        raise NotImplementedError("Connect to agent.ceo API — see https://agent.ceo/docs")


class AgentMCPServer:
    """MCP server with built-in agent.ceo platform integration.

    Create MCP servers that expose tools, resources, and prompts
    to AI agents running in a Cyborgenic Organization.

    Example:
        server = AgentMCPServer(name="my-tools")

        @server.tool()
        async def greet(name: str) -> str:
            return f"Hello, {name}!"

        server.run()
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        agent_ceo_token: str | None = None,
        organization_id: str | None = None,
    ):
        self.name = name
        self.description = description
        self.agent_ceo = AgentCEOClient(
            token=agent_ceo_token,
            organization_id=organization_id,
        )
        self._tools: dict[str, ToolDefinition] = {}
        self._resources: dict[str, Callable] = {}
        self._prompts: dict[str, Callable] = {}

    def tool(self, name: str | None = None, description: str | None = None):
        """Register a function as an MCP tool.

        Args:
            name: Override the tool name (defaults to function name).
            description: Override the description (defaults to docstring).
        """

        def decorator(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            tool_name = name or fn.__name__
            tool_desc = description or fn.__doc__ or ""

            # Extract parameter schema from type hints
            sig = inspect.signature(fn)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                annotation = param.annotation
                param_type = "string"  # default
                if annotation == int:
                    param_type = "integer"
                elif annotation == float:
                    param_type = "number"
                elif annotation == bool:
                    param_type = "boolean"
                params[param_name] = {"type": param_type}

            self._tools[tool_name] = ToolDefinition(
                name=tool_name,
                description=tool_desc,
                handler=fn,
                parameters=params,
            )
            return fn

        return decorator

    def resource(self, uri_template: str):
        """Register a function as an MCP resource."""

        def decorator(fn: Callable) -> Callable:
            self._resources[uri_template] = fn
            return fn

        return decorator

    def prompt(self, name: str | None = None):
        """Register a function as an MCP prompt template."""

        def decorator(fn: Callable) -> Callable:
            prompt_name = name or fn.__name__
            self._prompts[prompt_name] = fn
            return fn

        return decorator

    async def _handle_request(self, request: dict) -> dict:
        """Handle an incoming MCP JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": self.name, "version": "0.1.0"},
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"listChanged": False},
                    "prompts": {"listChanged": False},
                },
            }

        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": {
                            "type": "object",
                            "properties": t.parameters,
                        },
                    }
                    for t in self._tools.values()
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            if tool_name not in self._tools:
                return {"error": {"code": -32602, "message": f"Unknown tool: {tool_name}"}}
            handler = self._tools[tool_name].handler
            result = await handler(**arguments)
            return {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}

        return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

    async def _run_stdio(self):
        """Run the server using stdio transport (default for MCP)."""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            try:
                request = json.loads(line.decode())
                result = await self._handle_request(request)
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)},
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

    def run(self, transport: str = "stdio", host: str = "localhost", port: int = 8080):
        """Start the MCP server.

        Args:
            transport: "stdio" (default) or "sse" for HTTP Server-Sent Events.
            host: Host to bind to (SSE transport only).
            port: Port to bind to (SSE transport only).
        """
        if transport == "stdio":
            asyncio.run(self._run_stdio())
        elif transport == "sse":
            # TODO: Implement SSE transport
            raise NotImplementedError("SSE transport coming soon — see https://agent.ceo/docs")
        else:
            raise ValueError(f"Unknown transport: {transport}. Use 'stdio' or 'sse'.")
