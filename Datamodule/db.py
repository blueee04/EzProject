import pymongo
from pymongo import MongoClient
from typing import Optional
import tracemalloc
client = MongoClient("mongodb+srv://hegdeadithyak:adi4720Q@prjct.0cc2j4d.mongodb.net/")
if client:
    print("Connected to the MongoDB Atlas!")
db = client["discord"]
collection = db["tasks"]


def add(project_id: int, task_description: str,status : Optional[str] = "ic"):
    
    if status == "c":
        collection.insert_one(
            {
                "project_id": project_id,
                "task_id": task_id(project_id),
                "description": task_description,
                "status": "complete \u2705"
            }
        )

    collection.insert_one(
        {
            "project_id": project_id,
            "task_id": task_id(project_id),
            "description": task_description,
            "status": "incomplete \u274C"
        }
    )



def list_task(project_id):
    if project_id not in collection.distinct("project_id"):
        return "No tasks found"
    else:
        project_ids = collection.find({"project_id": project_id})
        project_descriptions = [f"{i}. {task['description']} - {task['status']}" for i,task in enumerate(project_ids)]
        return project_descriptions

        
    
def edit(project_id, task_id, task_description, status):
    if status == "c":
        collection.update_one(
            {"project_id": project_id, "task_id": task_id},
            {"$set": {"description": task_description, "status": "complete \u2705"}},
        )
    else:
        collection.update_one(
        {"project_id": project_id, "task_id": task_id},
        {"$set": {"description": task_description}},
        )

def task_id(project_id):

    project_id = collection.find({"project_id": project_id})
    task_ids = [task["task_id"] for task in project_id]
    if(len(task_ids)==0):
        return 1
    task_ids.sort()
    return task_ids[-1]+1

async def delete_task(project_id, task_id):
    tracemalloc.start()
    await collection.delete_one({"project_id": project_id, "task_id": task_id})
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

def delete_project(project_id):
    collection.delete_many({"project_id": project_id})
# print(task_id(2))
