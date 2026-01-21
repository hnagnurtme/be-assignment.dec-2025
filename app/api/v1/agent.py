from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agent.agent import AgentService
from app.schemas.common import ApiResponse
from app.core.auth import get_current_user
from app.models.user import User
from app.dependencies import AgentSvc

router = APIRouter(tags=["AI Agent"])

class AgentQueryRequest(BaseModel):
    query: str

class AgentQueryResponse(BaseModel):
    answer: str

@router.post("/agent/query", response_model=ApiResponse[AgentQueryResponse])
async def query_agent(
    query_request: AgentQueryRequest,
    agent_service: AgentSvc
):
    """Query the Task AI Agent using natural language."""
    answer = await agent_service.query(query_request.query)
    return ApiResponse(
        message="Agent responded successfully",
        data=AgentQueryResponse(answer=answer)
    )
