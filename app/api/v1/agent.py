from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.agent.service import AgentService
from app.schemas.common import ApiResponse

router = APIRouter(tags=["AI Agent"])

class AgentQueryRequest(BaseModel):
    query: str

class AgentQueryResponse(BaseModel):
    answer: str

def get_agent_service():
    return AgentService()

@router.post("/agent/query", response_model=ApiResponse[AgentQueryResponse])
async def query_agent(
    request: AgentQueryRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Query the Task AI Agent using natural language."""
    answer = await agent_service.query(request.query)
    return ApiResponse(
        message="Agent responded successfully",
        data=AgentQueryResponse(answer=answer)
    )
