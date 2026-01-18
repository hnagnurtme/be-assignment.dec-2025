# System Design for Task Management System

Based on the `README.md` requirements, this document outlines the system architecture, component interactions, and the specific design for the MCP (Model Context Protocol) and AI Agent integration.

## 1. High-Level Architecture (Deployment View)

The system follows a microservices-lite architecture containerized with Docker.

```mermaid
graph TD
    Client[Client Apps\n(Web / Mobile / Postman)] -->|HTTP/HTTPS| Nginx[Nginx\n(Reverse Proxy)]
    
    subgraph "Docker Network"
        Nginx -->|Proxy Pass :8000| API[FastAPI Backend\n(App + MCP Server)]
        
        API -->|Read/Write| DB[(PostgreSQL\nPrimary Data)]
        API -->|Cache / PubSub| Redis[(Redis\nCache & Queue)]
        
        Agent[Task AI Agent\n(Python Script / Service)] -.->|MCP Protocol| API
        
        API -.->|Introspection| API_Self[API Routes]
    end
    
    Agent -->|API Call| LLM[LLM Provider\n(OpenAI / Groq / Anthropic)]
```

### Components Description
1.  **Nginx**: Acts as the entry point, handling SSL termination (optional), static files (if any), and forwarding API requests to the backend.
2.  **FastAPI Backend**:
    *   **Core API**: REST endpoints for User, Project, Task management.
    *   **MCP Server**: An adapter layer that converts these REST endpoints into "Tools" that the AI Agent can understand and invoke.
3.  **PostgreSQL**: relational database storing users, organizations, projects, tasks, comments, etc.
4.  **Redis**:
    *   **Caching**: Caching frequent queries (e.g., getting task lists).
    *   **Notifications**: Could be used as a message broker if implementing real-time notifications, or simple key-value storage for unread counts.
5.  **Task AI Agent**: A standalone client or service that:
    *   Connects to the MCP Server (running within or alongside FastAPI).
    *   Accepts natural language input.
    *   Uses an LLM to decide which MCP Tool (API endpoint) to call.

## 2. Component Design & Logical Flow

### 2.1 Backend Layers
*   **API Layer (`app/api`)**: Standard FastAPI routers.
*   **Service Layer (`app/services`)**: Business logic (e.g., "Check if user has permission", "Calculate overdue status").
*   **Repository Layer (`app/repositories`)**: Database abstractions (CRUD operations via SQLAlchemy).
*   **Models (`app/models`)**: SQLAlchemy ORM classes.

### 2.2 MCP Server & AI Agent Integration (Crucial Requirement)

This is the advanced part of the assignment.
*   **Auto-Conversion**: We need a mechanism (like `mcp-server-fastapi` or custom introspection) that iterates over `app.routes`.
*   **Mapping**:
    *   `POST /tasks/` -> Tool: `create_task(title, description, ...)`
    *   `GET /tasks/` -> Tool: `list_tasks(status, priority, ...)`
*   **Flow**:
    1.  User asks Agent: "Create a high priority task for 'Fix Bug' for John".
    2.  Agent sends prompt to LLM.
    3.  LLM responds with "Tool Call: `create_task(title='Fix Bug', priority='high', assignee='John')`".
    4.  Agent executes this tool against the FastAPI MCP Server.
    5.  MCP Server calls the actual service logic.
    6.  Result is returned to Agent -> LLM -> User.

## 3. Data Flow Example: Task Creation

1.  **Request**: `POST /api/v1/tasks` (with JWT Token).
2.  **Middleware**: `AuthMiddleware` verifies JWT and extracts `user_id`.
3.  **Controller**: `TasksRouter` validates input payload (Pydantic).
4.  **Service**: `TaskService`:
    *   Checks if user is a member of the project.
    *   Create Task object.
5.  **Repository**: `TaskRepo` saves to PostgreSQL.
6.  **Post-Action**:
    *   Create "Notification" record for the assignee.
    *   Invalidate relevant Redis caches.
7.  **Response**: Return created Task JSON.

## 4. What You Need To Do (Action Plan)

To fulfill the "System Design" deliverable:

1.  **Understand this architecture**: Know how the containerized services talk to each other (defined in `docker-compose.yml`).
2.  **Implement the Logic**:
    *   Finish the CRUD API.
    *   Implement the MCP Server adapter (Section C1 in README).
    *   Build the AI Agent script (Section C2 in README).
3.  **Documentation**: This file serves as your System Design documentation.
