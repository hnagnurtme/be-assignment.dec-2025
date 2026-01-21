import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.agent.service import AgentService

# Mock API keys for Pydantic validation
os.environ["GROQ_API_KEY"] = "gsk_test_key_1234567890abcdef1234567890abcdef"
os.environ["OPENAI_API_KEY"] = "sk-test-key-1234567890abcdef1234567890abcdef"

def generate_test_token():
    import jwt
    from datetime import datetime, timedelta
    payload = {
        "sub": "1",
        "email": "test@example.com",
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "test-secret-key", algorithm="HS256")

client = TestClient(app)

class TestAgent:

    @pytest.mark.asyncio
    @patch("app.agent.service.AgentExecutor.ainvoke")
    async def test_agent_service_query(self, mock_ainvoke):
        """Test the AgentService query logic."""
        # Arrange
        mock_ainvoke.return_value = {"output": "I can help you with tasks."}
        service = AgentService(provider="groq")
        
        # Act
        response = await service.query("Hello")
        
        # Assert
        assert response == "I can help you with tasks."
        mock_ainvoke.assert_called_once()

    @patch("app.agent.service.AgentExecutor.ainvoke")
    def test_agent_api_endpoint(self, mock_ainvoke):
        """Test the Agent API endpoint."""
        # Arrange
        mock_ainvoke.return_value = {"output": "Task created."}
        token = generate_test_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Act
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Create a task"},
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["answer"] == "Task created."

    @pytest.mark.asyncio
    async def test_agent_init_provider(self):
        """Test agent initialization with different providers."""
        with patch("app.agent.service.ChatGroq") as mock_groq:
            AgentService(provider="groq")
            mock_groq.assert_called_once()
            
        with patch("app.agent.service.ChatOpenAI") as mock_openai:
            AgentService(provider="openai")
            mock_openai.assert_called_once()
