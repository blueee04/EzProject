import pymongo
from pymongo import MongoClient
from typing import Optional
import tracemalloc
from config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


def add(project_id: int, task_description: str, status: Optional[str] = "ic"):
    if status == "c":
        status_text = "complete \u2705"
    else:
        status_text = "incomplete \u274C"
    
    collection.insert_one(
        {
            "project_id": project_id,
            "task_id": task_id(project_id),
            "description": task_description,
            "status": status_text
        }
    )

def list_task(project_id):
    if project_id not in collection.distinct("project_id"):
        return ["No tasks found"]
    else:
        project_tasks = collection.find({"project_id": project_id})
        project_descriptions = [f"{task['task_id']}. {task['description']} - {task['status']}" for task in project_tasks]
        return project_descriptions

def edit(project_id, task_id, task_description, status):
    update_data = {"description": task_description}
    
    if status == "complete \u2705":
        update_data["status"] = "complete \u2705"
    elif status == "incomplete \u274C":
        update_data["status"] = "incomplete \u274C"
    
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

