import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb+srv://hegdeadithyak:adi4720Q@prjct.0cc2j4d.mongodb.net/")
if client:
    print("Connected to the MongoDB Atlas!")
db = client["discord"]
collection = db["tasks"]


def add(project_id, task_description,Tasks,status = "incomplete"):
    Tasks.setdefault(project_id, []).append(task_description)
    if status == "c":
        collection.insert_one(
            {
                "project_id": project_id,
                "task_id": len(Tasks[project_id]),
                "description": task_description,
                "status": "complete \u2705"
            }
        )

    collection.insert_one(
        {
            "project_id": project_id,
            "task_id": len(Tasks[project_id]),
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

        
    
def edit(project_id, task_id, task_description, Tasks):
    Tasks[project_id][task_id - 1] = task_description
    collection.update_one(
        {"project_id": project_id, "task_id": task_id},
        {"$set": {"description": task_description}},
    )

list_task(3)