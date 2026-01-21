import pytest
from fastapi import FastAPI
from app.mcp.server import MCPServer

@pytest.mark.asyncio
async def test_mcp_tool_discovery():
    """Test that the MCP server discovers FastAPI routes."""
    # Arrange
    app = FastAPI()
    
    @app.get("/test-tool", summary="A test tool")
    async def test_tool():
        return {"message": "hello"}
        
    mcp_server = MCPServer(app)
    
    # Act
    # Find the list_tools handler
    from mcp.types import ListToolsRequest
    handler = mcp_server.server.request_handlers.get(ListToolsRequest)
    
    assert handler is not None
    tools_result = await handler(ListToolsRequest())
    tools = tools_result.root.tools
    
    # Assert
    assert len(tools) > 0
    # Check if our test tool is in the list
    tool_names = [t.name for t in tools]
    assert "get_test-tool" in tool_names
    
    # Verify description
    test_tool_data = next(t for t in tools if t.name == "get_test-tool")
    assert test_tool_data.description == "A test tool"

@pytest.mark.asyncio
async def test_mcp_call_tool_mock():
    """Test the tool calling structure."""
    app = FastAPI()
    mcp_server = MCPServer(app)
    
    # Act
    from mcp.types import CallToolRequest, CallToolRequestParams
    handler = mcp_server.server.request_handlers.get(CallToolRequest)
    assert handler is not None
    
    params = CallToolRequestParams(name="get_test", arguments={"arg": 1})
    result = await handler(CallToolRequest(params=params))
    
    # Assert
    assert len(result.root.content) == 1
    assert "Executed tool get_test" in result.root.content[0].text
