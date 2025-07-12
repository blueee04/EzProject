import pymongo
from pymongo import MongoClient
from typing import Optional
import tracemalloc
from datetime import datetime, timedelta
from config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def add(project_id: int, task_description: str, status: Optional[str] = "ic", deadline: Optional[str] = None):
    if status == "c":
        status_text = "complete \u2705"
    else:
        status_text = "incomplete \u274C"
    
    task_data = {
        "project_id": project_id,
        "task_id": task_id(project_id),
        "description": task_description,
        "status": status_text
    }
    
    if deadline:
        task_data["deadline"] = deadline
    
    collection.insert_one(task_data)

def list_task(project_id):
    if project_id not in collection.distinct("project_id"):
        return ["No tasks found"]
    else:
        project_tasks = collection.find({"project_id": project_id})
        project_descriptions = []
        for task in project_tasks:
            task_desc = f"{task['task_id']}. {task['description']} - {task['status']}"
            if "deadline" in task:
                task_desc += f" (Due: {task['deadline']})"
            project_descriptions.append(task_desc)
        return project_descriptions

def edit(project_id, task_id, task_description, status, deadline: Optional[str] = None):
    update_data = {"description": task_description}
    
    if status == "complete \u2705":
        update_data["status"] = "complete \u2705"
    elif status == "incomplete \u274C":
        update_data["status"] = "incomplete \u274C"
    
    if deadline:
        update_data["deadline"] = deadline
    
    collection.update_one(
        {"project_id": project_id, "task_id": task_id},
        {"$set": update_data},
    )

def task_id(project_id):
    project_tasks = collection.find({"project_id": project_id})
    task_ids = [task["task_id"] for task in project_tasks]
    if len(task_ids) == 0:
        return 1
    task_ids.sort()
    return task_ids[-1] + 1

async def delete_task(project_id, task_id) -> None:
    collection.delete_many({"project_id": project_id, "task_id": task_id})

def delete_project(project_id):
    collection.delete_many({"project_id": project_id})

# Assignment functions
def assign_task_to_user(project_id: int, task_id: int, user_id: int) -> bool:
    """Assign a task to a user and store in database"""
    try:
        # First check if task exists
        task = collection.find_one({"project_id": project_id, "task_id": task_id})
        if not task:
            return False
        
        # Update the task with assignment
        collection.update_one(
            {"project_id": project_id, "task_id": task_id},
            {"$set": {"assigned_to": user_id}},
        )
        return True
    except Exception as e:
        print(f"Error assigning task: {e}")
        return False

def get_task_assignment(project_id: int, task_id: int) -> Optional[int]:
    """Get the user ID assigned to a task"""
    try:
        task = collection.find_one({"project_id": project_id, "task_id": task_id})
        if task and "assigned_to" in task:
            return task["assigned_to"]
        return None
    except Exception as e:
        print(f"Error getting task assignment: {e}")
        return None

def get_project_assignments(project_id: int) -> dict:
    """Get all assignments for a project"""
    try:
        tasks = collection.find({"project_id": project_id})
        assignments = {}
        for task in tasks:
            if "assigned_to" in task:
                assignments[task["task_id"]] = task["assigned_to"]
        return assignments
    except Exception as e:
        print(f"Error getting project assignments: {e}")
        return {}

def remove_task_assignment(project_id: int, task_id: int) -> bool:
    """Remove assignment from a task"""
    try:
        collection.update_one(
            {"project_id": project_id, "task_id": task_id},
            {"$unset": {"assigned_to": ""}},
        )
        return True
    except Exception as e:
        print(f"Error removing task assignment: {e}")
        return False

# Deadline functions
def set_task_deadline(project_id: int, task_id: int, deadline: str) -> bool:
    """Set a deadline for a task"""
    try:
        # First check if task exists
        task = collection.find_one({"project_id": project_id, "task_id": task_id})
        if not task:
            return False
        
        # Update the task with deadline
        collection.update_one(
            {"project_id": project_id, "task_id": task_id},
            {"$set": {"deadline": deadline}},
        )
        return True
    except Exception as e:
        print(f"Error setting deadline: {e}")
        return False

def get_overdue_tasks() -> list:
    """Get all overdue tasks"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        overdue_tasks = collection.find({
            "deadline": {"$lt": today},
            "status": {"$ne": "complete \u2705"}
        })
        return list(overdue_tasks)
    except Exception as e:
        print(f"Error getting overdue tasks: {e}")
        return []

def get_tasks_due_soon(days: int = 3) -> list:
    """Get tasks due within the next N days"""
    try:
        today = datetime.now()
        future_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        due_soon_tasks = collection.find({
            "deadline": {"$gte": today.strftime("%Y-%m-%d"), "$lte": future_date},
            "status": {"$ne": "complete \u2705"}
        })
        return list(due_soon_tasks)
    except Exception as e:
        print(f"Error getting tasks due soon: {e}")
        return []

def get_task_deadline(project_id: int, task_id: int) -> Optional[str]:
    """Get the deadline for a specific task"""
    try:
        task = collection.find_one({"project_id": project_id, "task_id": task_id})
        if task and "deadline" in task:
            return task["deadline"]
        return None
    except Exception as e:
        print(f"Error getting task deadline: {e}")
        return None

def remove_task_deadline(project_id: int, task_id: int) -> bool:
    """Remove deadline from a task"""
    try:
        collection.update_one(
            {"project_id": project_id, "task_id": task_id},
            {"$unset": {"deadline": ""}},
        )
        return True
    except Exception as e:
        print(f"Error removing task deadline: {e}")
        return False

