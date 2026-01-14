"""Endpoint documentation - summaries, descriptions for OpenAPI/Swagger."""


class AuthDocs:
    """Documentation for authentication endpoints."""

    class Register:
        SUMMARY = "Register a new user"
        DESCRIPTION = (
            "Register a new user with a new organization. "
            "The registering user becomes the organization admin."
        )

    class Login:
        SUMMARY = "Login user"
        DESCRIPTION = "Authenticate with email and password to receive JWT tokens."

    class Refresh:
        SUMMARY = "Refresh access token"
        DESCRIPTION = "Use refresh token to get a new access token."

    class Logout:
        SUMMARY = "Logout user"
        DESCRIPTION = "Invalidate the current session and tokens."


class UserDocs:
    """Documentation for user endpoints."""

    class GetMe:
        SUMMARY = "Get current user"
        DESCRIPTION = "Get the profile of the currently authenticated user."

    class UpdateMe:
        SUMMARY = "Update current user"
        DESCRIPTION = "Update the profile of the currently authenticated user."

    class GetById:
        SUMMARY = "Get user by ID"
        DESCRIPTION = "Get a user's public profile by their ID."

    class List:
        SUMMARY = "List users"
        DESCRIPTION = "Get a paginated list of users in the organization."


class OrganizationDocs:
    """Documentation for organization endpoints."""

    class Get:
        SUMMARY = "Get organization"
        DESCRIPTION = "Get the current user's organization details."

    class Update:
        SUMMARY = "Update organization"
        DESCRIPTION = "Update organization details. Requires admin role."

    class ListMembers:
        SUMMARY = "List organization members"
        DESCRIPTION = "Get a paginated list of members in the organization."

    class InviteMember:
        SUMMARY = "Invite member"
        DESCRIPTION = "Invite a new member to the organization. Requires admin role."

    class RemoveMember:
        SUMMARY = "Remove member"
        DESCRIPTION = "Remove a member from the organization. Requires admin role."


class ProjectDocs:
    """Documentation for project endpoints."""

    class Create:
        SUMMARY = "Create project"
        DESCRIPTION = "Create a new project in the organization."

    class Get:
        SUMMARY = "Get project"
        DESCRIPTION = "Get project details by ID."

    class Update:
        SUMMARY = "Update project"
        DESCRIPTION = "Update project details."

    class Delete:
        SUMMARY = "Delete project"
        DESCRIPTION = "Delete a project. Requires manager or admin role."

    class List:
        SUMMARY = "List projects"
        DESCRIPTION = "Get a paginated list of projects in the organization."

    class AddMember:
        SUMMARY = "Add project member"
        DESCRIPTION = "Add a member to the project."

    class RemoveMember:
        SUMMARY = "Remove project member"
        DESCRIPTION = "Remove a member from the project."


class TaskDocs:
    """Documentation for task endpoints."""

    class Create:
        SUMMARY = "Create task"
        DESCRIPTION = "Create a new task in a project."

    class Get:
        SUMMARY = "Get task"
        DESCRIPTION = "Get task details by ID."

    class Update:
        SUMMARY = "Update task"
        DESCRIPTION = "Update task details."

    class Delete:
        SUMMARY = "Delete task"
        DESCRIPTION = "Delete a task."

    class List:
        SUMMARY = "List tasks"
        DESCRIPTION = "Get a paginated list of tasks with optional filters."

    class Assign:
        SUMMARY = "Assign task"
        DESCRIPTION = "Assign a task to a user."

    class UpdateStatus:
        SUMMARY = "Update task status"
        DESCRIPTION = "Update the status of a task (todo, in-progress, done)."


class HealthDocs:
    """Documentation for health check endpoints."""

    class Check:
        SUMMARY = "Health check"
        DESCRIPTION = "Check if the API is running."

    class Database:
        SUMMARY = "Database health check"
        DESCRIPTION = "Check database connectivity."

    class Redis:
        SUMMARY = "Redis health check"
        DESCRIPTION = "Check Redis connectivity."
