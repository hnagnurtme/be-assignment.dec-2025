import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from app.agent.db_helper import get_sync_session
from app.models.project import Project  
from app.models.task import Task, TaskPriority, TaskStatus


def parse_input(args: Any, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Robustly parse LLM input (JSON or KV pairs) into a dictionary."""
    if args and isinstance(args[0], str):
        input_str = args[0]
        try:
            # Try parsing as JSON first
            data = json.loads(input_str)
            if isinstance(data, dict):
                kwargs.update(data)
        except json.JSONDecodeError:
            # Fallback: simple key=value parsing
            lines = [line.strip() for line in input_str.split('\n') if '=' in line]
            for line in lines:
                k, v = line.split('=', 1)
                clean_k = k.strip().strip("'").strip('"')
                clean_v = v.strip().strip("'").strip('"')
                kwargs[clean_k] = clean_v
    return kwargs


def create_task_sync(
    user_id: int,
    organization_id: int,
    *args: Any,
    **kwargs: Any
) -> str:
    """Synchronous task creation - creates own DB session."""
    params = parse_input(args, kwargs)
    title = params.get('title', '')
    project = params.get('project', '')
    description = params.get('description', '')
    priority = params.get('priority', 'medium')
    due_date = params.get('due_date', '')

    session = get_sync_session()
    try:
        if not title:
            return "❌ Error: Task title is required."
        if not project:
            return "❌ Error: Project name is required."
        
        proj = session.query(Project).join(
            Project.members
        ).filter(
            Project.name.ilike(project),
            Project.organization_id == organization_id
        ).first()
        
        if not proj:
            return f"❌ Error: Project '{project}' not found or you don't have access to it."
        
        due_date_obj = None
        if due_date:
            try:
                if due_date.lower() in ["next friday", "friday", "today"]:
                    due_date_obj = datetime.now() + timedelta(days=7 if due_date.lower() != "today" else 0)
                else:
                    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                pass # Accept missing/invalid date gracefully
        
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.HIGH
        }
        task_priority = priority_map.get(priority.lower() if isinstance(priority, str) else "medium", TaskPriority.MEDIUM)
        
        task = Task(
            title=title,
            description=description,
            priority=task_priority,
            status=TaskStatus.TODO,
            project_id=proj.id,
            created_by_id=user_id,
            due_date=due_date_obj
        )
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return f"✅ Successfully created task '{task.title}' (ID: {task.id}) in project '{proj.name}'."
        
    except Exception as e:
        session.rollback()
        return f"❌ Error creating task: {str(e)}"
    finally:
        session.close()


def list_tasks_sync(user_id: int, organization_id: int, *args: Any, **kwargs: Any) -> str:
    """List tasks in a project - synchronous."""
    params = parse_input(args, kwargs)
    project = params.get('project', '')

    session = get_sync_session()
    try:
        if not project:
            return "❌ Error: Project name is required."

        proj = session.query(Project).join(
            Project.members
        ).filter(
            Project.name.ilike(project),
            Project.organization_id == organization_id
        ).first()
        
        if not proj:
            return f"❌ Error: Project '{project}' not found."
        
        tasks = session.query(Task).filter(Task.project_id == proj.id).all()
        
        if not tasks:
            return f"No tasks found in project '{project}'."
        
        task_details = [f"- [{t.status.value}] {t.title} ({t.priority.value})" for t in tasks]
        return f"Tasks in '{proj.name}':\n" + "\n".join(task_details)
        
    except Exception as e:
        return f"❌ Error listing tasks: {str(e)}"
    finally:
        session.close()


def get_overdue_tasks_sync(user_id: int, organization_id: int, *args: Any, **kwargs: Any) -> str:
    """Get overdue tasks - synchronous."""
    session = get_sync_session()
    try:
        now = datetime.now()
        tasks = session.query(Task).join(Project).filter(
            Project.organization_id == organization_id,
            Task.due_date < now,
            Task.status != TaskStatus.DONE
        ).all()
        
        if not tasks:
            return "No overdue tasks found."
        
        task_details = [f"- {t.title} (due: {t.due_date.strftime('%Y-%m-%d')})" for t in tasks]
        return f"Overdue tasks:\n" + "\n".join(task_details)
        
    except Exception as e:
        return f"❌ Error getting overdue tasks: {str(e)}"
    finally:
        session.close()
