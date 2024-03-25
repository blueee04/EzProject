import discord
import numpy as np
import re

#pymongo module
from pymongo import MongoClient


client = MongoClient("mongodb+srv://hegdeadithyak:adi4720Q@prjct.0cc2j4d.mongodb.net/")
if client:
    print("Connected to the MongoDB Atlas!")
db = client["discord"]
collection = db["tasks"]


# discord.py module
from discord.ext import commands

bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"

# Bot instance
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


def split_string_with_space(string):
    words = re.split(r"\s+", string)
    words = [word for word in words if word]
    return words


# Bot event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")


Tasks = {}
status = {}


@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    if message.author == bot.user:
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("!addtask"):
        try:
            msg = message.content.split("!addtask ", 1)[1]
            print(msg)
            stuff = split_string_with_space(msg)
            proj_id = int(stuff[0])
            if proj_id not in Tasks:
                Tasks[proj_id] = []
                status[proj_id] = []
            task_string = ""
            for i in range(1, len(stuff)):
                task_string += stuff[i] + " "
            Tasks[proj_id].append(task_string)
            status[proj_id].append({task_string: "incomplete \u274C"})
            client["discord"]["tasks"].insert_one(
                {
                    "project_id": proj_id,
                    "task_id": len(Tasks[proj_id]),
                    "description": task_string,
                }
            )
            await message.channel.send("Task added!")
        except:
            await message.channel.send(
                f"{message.author.mention} Please enter in the format **!addtask <proj_id> <task>**"
            )

    if message.content.startswith("!listtask"):
        try:
            msg = message.content.split("!listtask ", 1)[1]
            proj_id = int(msg)
            if proj_id not in Tasks:
                await message.channel.send("No tasks found")
            else:
                Tasks  = client["discord"]["tasks"].find({"project_id": proj_id})
                task = [
                    f"{i+1}. {task} - {status}"
                    for i, (task, status) in enumerate(
                        zip(Tasks[proj_id], status[proj_id])
                    )
                ]
                await message.channel.send(
                    f"List of Tasks for Project ID : {proj_id} is : \n"
                    + "\n".join(task)
                )
        except:
            await message.channel.send(
                f"{message.author.mention} Please enter in the format !listtask <proj_id>"
            )

    if message.content.startswith("!edittask"):
        msg = message.content.split("!edittask ", 1)[1]

        try:
            stuff = split_string_with_space(msg)
            proj_id = int(stuff[0])
            task_id = int(stuff[1])
            task_string = ""
            for i in range(2, len(stuff)):
                task_string += stuff[i] + " "
            Tasks[proj_id][task_id - 1] = task_string
            status[proj_id][task_id - 1] = {task_string: "incomplete \u274C"}
            client["discord"]["tasks"].update_one(
                {"project_id": proj_id, "task_id": task_id},
                {"$set": {"description": task_string}},
            )
            await message.channel.send("Task edited!")
        except:
            await message.channel.send(
                f"{message.author.mention} Please enter in the format !edittask <proj_id> <task_id> <new_task>"
            )

    await bot.process_commands(message)


bot.run(bot_token)
