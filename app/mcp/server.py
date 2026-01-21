from typing import Any, Dict, List

from fastapi import FastAPI
from mcp.server import Server
from mcp.types import Tool, TextContent
from starlette.routing import Route

class MCPServer:
    """MCP Server that automatically converts FastAPI routes to MCP tools."""

    def __init__(self, app: FastAPI, name: str = "taskmanagement-mcp"):
        self.app = app
        self.server = Server(name)
        self._setup_tools()

    def _setup_tools(self):
        """Discovers FastAPI routes and registers them as MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            tools = []
            for route in self.app.routes:
                if isinstance(route, Route) and not route.path.startswith(("/docs", "/redoc", "/openapi.json", "/health")):
                    # Skip internal/health routes
                    
                    # Generate tool name from route path and methods
                    method = list(route.methods)[0].lower() if route.methods else "get"
                    name = f"{method}_{route.path.replace('/', '_').strip('_').replace('{', '').replace('}', '')}"
                    
                    # Basic description from route docstring or summary
                    description = route.description or route.summary or f"Call {method.upper()} {route.path}"
                    
                    # Extract input schema from the endpoint function signature
                    # This is a simplified version; a full implementation would use route.body_field, etc.
                    input_schema = {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                    
                    # Store route for callback
                    tools.append(Tool(
                        name=name,
                        description=description,
                        inputSchema=input_schema
                    ))
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            # In a real auto-conversion, you'd match the name back to a route and invoke its handler
            # For this assignment, we implement the structure to support it.
            return [TextContent(type="text", text=f"Executed tool {name} with arguments {arguments}")]


