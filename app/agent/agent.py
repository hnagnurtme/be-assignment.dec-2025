import logging
from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

from app.models.user import User

# Configure logger
logger = logging.getLogger(__name__)


class AgentService:
    """Service for the Task AI Agent."""

    def __init__(
        self,
        current_user: User,
        provider: str = "groq",
        **kwargs # Accept other dependencies but we don't need them now
    ) -> None:
        self.current_user = current_user
        self.llm = self._init_llm(provider)
        self.tools = self._init_tools()
        self.agent_executor = self._setup_agent()

    def _init_llm(self, provider: str):
        from app.config import settings
        
        if provider == "groq":
            return ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.groq_model,
                streaming=False
            )
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            streaming=False
        )

    def _init_tools(self) -> List[StructuredTool]:
        """Initialize LangChain tools with proper schemas."""
        
        class CreateTaskInput(BaseModel):
            title: str = Field(description="Title of the task")
            project: str = Field(default="", description="Project name")
            description: str = Field(default="", description="Task description")
            priority: str = Field(default="medium", description="Priority (low, medium, high)")
            due_date: str = Field(default="", description="Due date (YYYY-MM-DD)")
        
        class ListTasksInput(BaseModel):
            project: str = Field(default="", description="Project name")
        
        class GetOverdueTasksInput(BaseModel):
            filter: str = Field(default="", description="Optional filter")
        
        def sync_create_task(*args, **kwargs):
            from app.agent.tools_sync import create_task_sync
            return create_task_sync(
                self.current_user.id,
                self.current_user.organization_id,
                *args, **kwargs
            )
        
        def sync_list_tasks(*args, **kwargs):
            from app.agent.tools_sync import list_tasks_sync
            return list_tasks_sync(
                self.current_user.id,
                self.current_user.organization_id,
                *args, **kwargs
            )
        
        def sync_get_overdue_tasks(*args, **kwargs):
            from app.agent.tools_sync import get_overdue_tasks_sync
            return get_overdue_tasks_sync(
                self.current_user.id,
                self.current_user.organization_id,
                *args, **kwargs
            )
        
        return [
            StructuredTool(
                name="create_task",
                func=sync_create_task,
                description="Create a task. Input: JSON object with 'title' and 'project'. Options: 'description', 'priority', 'due_date'.",
                args_schema=CreateTaskInput
            ),
            StructuredTool(
                name="list_tasks",
                func=sync_list_tasks,
                description="List tasks in a project. Input: JSON object with 'project'.",
                args_schema=ListTasksInput
            ),
            StructuredTool(
                name="get_overdue_tasks",
                func=sync_get_overdue_tasks,
                description="Get overdue tasks. Input: JSON object with optional 'filter'.",
                args_schema=GetOverdueTasksInput
            )
        ]

    def _setup_agent(self):
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be a VALID JSON object)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True
        )

    async def query(self, user_input: str) -> str:
        """Process a natural language query."""
        try:
            logger.info(f"Agent processing query: {user_input}")
            response = await self.agent_executor.ainvoke({"input": user_input})
            return response.get("output", "I couldn't generate a response. Please try rephrasing.")
        except Exception as e:
            logger.error(f"Agent query failed: {str(e)}", exc_info=True)
            return f"Error processing your request: {str(e)}"
