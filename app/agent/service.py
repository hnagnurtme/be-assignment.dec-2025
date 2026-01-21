import os
from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool as LCTool



class AgentService:
    """Service for the Task AI Agent."""

    def __init__(self, provider: str = "groq"):
        self.llm = self._init_llm(provider)
        self.tools = self._init_tools()
        self.agent_executor = self._setup_agent()

    def _init_llm(self, provider: str):
        if provider == "groq":
            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama3-70b-8192"
            )
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4-turbo-preview"
        )

    def _init_tools(self) -> List[LCTool]:
        """Convert MCP tools into LangChain tools."""
        # This is a conceptual bridge. In a real scenario, we'd pull these from the MCP server
        # or directly wrap the service methods for better performance.
        return [
            LCTool(
                name="list_tasks",
                func=lambda x: "Listing tasks from database...",
                description="List all tasks in a project."
            ),
            LCTool(
                name="create_task",
                func=lambda x: "Task created successfully.",
                description="Create a new task in a project."
            ),
            LCTool(
                name="get_overdue_tasks",
                func=lambda x: "Found 2 overdue tasks.",
                description="Get a list of overdue tasks."
            )
        ]

    def _setup_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful Task Management Assistant. You can manage tasks, projects, and organizations."),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def query(self, user_input: str) -> str:
        """Process a natural language query."""
        response = await self.agent_executor.ainvoke({"input": user_input})
        return response["output"]
