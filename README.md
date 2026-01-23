# 📑 Intern Backend Developer Assignment

- Copyright (c) River Flow Solutions, Jsc. 2026. All rights reserved.
- We only use the submissions for candidates evaluation.

## **A. Instructions**
- Submission:
  - Candidate must fork this repository to a public repo under their name for submission. Notify email `hr@riverflow.solutions` when done.
  - The repository must be public and accessible to the public.
  - Mark the "Review Criteria" items as done when you have completed the requirements.
  - **Note**: If you are concerned about others copying your assignment, you may choose to push your code only on the deadline day. Please note, however, that we check the commit log history to verify contributions.


- Build a **multi-organization Task Management backend** (organizations → projects → tasks) with basic collaboration and notifications.  
- **Stack**: Python, FastAPI, PostgreSQL, Redis, Nginx.
- Use Justfile (https://github.com/casey/just) for all run and development commands.
- Use Docker for deployment.
- Deliverables: GitHub repo, ER + System design diagrams, Dockerized deployment, README.
- **Advanced**: Build a Task AI Agent that integrates with the MCP server and LLM models (Groq, OpenAI, etc.) to test and interact with MCP tools. See section C2 for details. 

---

## **B. Task Management Requirements & Use Cases**

### **B1. Functional Scope**
- **Organizations & Users**
  - Each user belongs to an organization.  
  - Roles: **Admin**, **Manager**, **Member**.  

- **Projects**
  - Belong to one organization.  
  - Can add/remove members.  
  - Admin/Manager can create projects, Members can only participate.  

- **Tasks**
  - CRUD operations.  
  - Belong to a project.  
  - Fields: title, description, status (`todo/in-progress/done`), priority (`low/medium/high`), due_date, assignee.  
  - Status workflow: `todo → in-progress → done` (no complex review step).  

- **Collaboration**
  - Users can comment on tasks.  
  - Users can upload simple file attachments (local storage).  

- **Notifications**
  - Users receive a notification when:  
    - They are assigned a task.  
    - Task status changes.  
    - A comment is added to their task.  

- **Reports (Basic)**
  - Count of tasks by status in a project.  
  - List of overdue tasks.  

---

### **B2. Use Cases**
1. **User Management**
   - Register/login with JWT.  
   - Admin adds users to the organization.  

2. **Project Management**
   - Create/list projects.  
   - Add/remove project members.  

3. **Task Management**
   - Create tasks with title, description, assignee, priority, due date.  
   - Update task status (`todo → in-progress → done`).  
   - List tasks in a project (filter by status, assignee, priority) with pagination support.  

4. **Collaboration**
   - Add comments to tasks.  
   - Upload attachment to a task.  

5. **Notifications**
   - Retrieve unread notifications.  
   - Mark notifications as read.  

6. **Reporting**
   - Get per-project task count by status.  
   - Get overdue tasks in a project.  

---

### **B3. Business Rules**
- Only project members can create or update tasks in that project.  
- Only Admin/Manager can assign tasks to others. Members can assign only to themselves.  
- Due date must be today or in the future (not past).  
- Task status can only progress forward (`todo → in-progress → done`), but not backward.  
- Attachments limited to 5MB each, max 3 per task.  

---

## **C. Tech Requirements**
- **Backend**: Python + FastAPI, SQLAlchemy, Alembic migrations.  
- **Database**: PostgreSQL with foreign keys + indexes.  
- **Cache/Notify**: Redis for caching task lists and storing notifications.  
- **Auth**: JWT (PyJWT) + role-based access (Admin/Manager/Member).  
- **Testing**: pytest with test containers or mocks for PostgreSQL & Redis. Specify your testing approach in the README.  
- **Deployment**: Docker + docker-compose (FastAPI + PostgreSQL + Redis + Nginx).  
- **MCP Server**: Convert FastAPI backend to MCP (Model Context Protocol) server using an auto-conversion approach. The MCP server must automatically discover and expose all FastAPI endpoints as MCP tools without requiring manual tool definitions for each endpoint. You may use packages like `fastmcp`, `mcp-server-fastapi`, or build a custom wrapper that introspects FastAPI routes. The MCP server must be tested using the Task AI Agent (see C2).  
- **AI Agent**: Langchain, langgraph, llama-index, openai, groq, anthropic, etc. (You can use any of these or a custom solution).

---

## **C1. MCP Server Conversion**

### **Requirements**
- Convert the FastAPI backend application to an MCP (Model Context Protocol) server.
- Use an auto-conversion approach (package or custom solution) to automatically expose all FastAPI endpoints as MCP tools.
- **Important**: The conversion must be automatic - do not manually define each tool. The solution should automatically discover FastAPI routes (via introspection) and convert them to MCP tools.
- The MCP server should handle:
  - All CRUD endpoints automatically
- **Testing**: MCP server must be tested using the Task AI Agent (see C2). The AI Agent will call MCP tools to verify functionality.
---

## **C2. Task AI Agent**

### **Overview**
Build an intelligent Task AI Agent that interacts with your task management system through the MCP server and leverages LLM models (Groq, OpenAI, Anthropic, etc.) to provide intelligent task management assistance. The AI Agent is also used to test and verify all MCP tools.

### **Requirements**
- **AI Agent Integration**: Create a Task AI Agent that connects to your MCP server to perform task management operations and test MCP tools.
- **LLM Integration**: Integrate with at least one LLM provider (Groq, OpenAI, Anthropic, etc.) to enable natural language understanding and task automation.
- **MCP Testing**: The agent must be used to test all MCP tools to verify they work correctly.
- **Agent Capabilities**: The agent should be able to:
  - Understand natural language requests about tasks (e.g., "Show me all high-priority tasks due this week")
  - Automatically create, update, or query tasks based on user instructions via MCP tools
  - Provide intelligent task suggestions and recommendations
  - Analyze task data and generate insights
  - Handle multi-step operations (e.g., "Create a task for John with high priority and set due date to next Friday")

### **Example Use Cases**
1. User: "Create a high-priority task for reviewing the Q4 report, assign it to Sarah, and set the due date to next Monday"
   - Agent interprets request → Calls MCP tools: create_task, update_task (assignee, priority, due_date)

2. User: "What are my overdue tasks and which ones should I prioritize?"
   - Agent queries tasks → Analyzes with LLM → Returns prioritized list with reasoning

3. User: "Show me all tasks in the 'Website Redesign' project that are in-progress"
   - Agent converts to MCP query → Returns filtered results


---

## **D. Review Criteria** (Total: 100 points)

### **D1. Core Requirements** (40 points)
- [x] Database schema with correct relations, constraints, and indexes. **(8 points)**
- [x] JWT auth with role-based permissions (Admin/Manager/Member). **(8 points)**
- [x] CRUD operations for Organizations, Projects, and Tasks with business rules enforced. **(12 points)**
- [x] Status workflow (`todo → in-progress → done`), comments, file attachments, and notifications working. **(8 points)**
- [x] Basic reporting endpoints (task counts by status, overdue tasks). **(4 points)**

### **D2. MCP Server & AI Agent** (20 points)
- [x] MCP server automatically exposes all FastAPI endpoints as tools (auto-conversion, no manual definitions). **(6 points)**
- [x] Task AI Agent implemented and integrated with MCP server. **(4 points)**
- [x] AI Agent successfully tests all MCP tools (create, read, update, delete operations). **(3 points)**
- [x] LLM integration working (at least one provider: Groq, OpenAI, Anthropic, etc.). **(3 points)**
- [x] Agent can interpret natural language and perform task operations via MCP tools. **(2 points)**
- [x] At least 3 agent features implemented (natural language task creation, querying, updates, etc.). **(2 points)**

### **D3. Code Quality & Testing** (20 points)
- [x] Centralized error handling, logging, and consistent API response format. **(6 points)**
- [x] Configurable via `.env`, pagination for list endpoints. **(4 points)**
- [x] Test coverage ≥ 70%. **(10 points)**

### **D4. Deployment & Documentation** (20 points)
- [x] Dockerized deployment with Nginx, PostgreSQL, Redis. **(10 points)**
- [x] Health check endpoints, environment variables configured. **(4 points)**
- [x] README with setup guide, API documentation (Swagger UI). **(6 points)**
