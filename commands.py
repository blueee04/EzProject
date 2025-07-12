import discord
from discord.ext import commands
from Datamodule.db import add, list_task, edit, delete_task, delete_project
import asyncio
from config import BOT_TOKEN, MONGODB_URI, DATABASE_NAME, COLLECTION_NAME

# MongoDB connection
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

intents = discord.Intents.default()
# Remove message_content for older discord.py versions
# intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Task descriptions and statuses
task_descriptions = {}
statuses = {}
assign = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"{ctx.author.mention} Hello!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'''{ctx.author.mention} Please enter the correct format
                         \n Format:
                         \n- /addtask **<project_id>** **<task_description>** **<status>**
                         \n- /listtask **<project_id>**
                         \n- /edittask **<project_id>** **<task_id>** **<new_task>** **<status>**''')

@bot.command(name="helpme")
async def help(ctx):
    await ctx.send(f'''{ctx.author.mention} Commands:
                         \n Format:
                         \n- /addtask **<project_id>** **<task_description>** **<status>**
                         \n- /listtask **<project_id>**
                         \n- /edittask **<project_id>** **<task_id>** **<new_task>** **<status>**
                         \n- /listall - List all projects
                         \n- /deletetask **<project_id>** **<task_id>**
                         \n- /deleteproject **<project_id>**
                         \n- /assign **<project_id>** **<task_id>** **<member>**''')

@bot.command(name="addtask")
async def add_task(ctx, project_id: int, *task_description: str, status="incomplete"):
    task_description = " ".join(task_description)
    temp_status = "ic"
    if status == "complete":
        temp_status = "c"
    add(project_id, task_description, temp_status)
    await ctx.send(f"{ctx.author.mention} Task added!")

@bot.command(name="listtask")
async def list_tasks(ctx, project_id: int):
    try:
        #if project id not found in the database
        if project_id not in collection.distinct("project_id"):
            await ctx.send("No tasks found")
            return
        
        task_list = list_task(project_id)
        
        await ctx.send(f"{ctx.author.mention} \n Tasks for project {project_id}:\n" + "\n".join(task_list))
    except:
        await ctx.send(f"{ctx.author.mention} Please enter a valid project ID,format: /listtask **<project_id>**")

@bot.command(name="listall")
async def list_all(ctx):
    try:
        #if project id not found in the database
        if len(collection.distinct("project_id"))==0:
            await ctx.send("No tasks found")
            return
        task_list = []
        for project_id in collection.distinct("project_id"):
            task_list.append(list_task(project_id))
        await ctx.send(f"{ctx.author.mention} \n Tasks for all projects:\n" + "\n".join(task_list))
    except:
        await ctx.send(f"{ctx.author.mention} Please enter a valid project ID,format: /listtask **<project_id>**")

@bot.command(name="edittask")
async def edit_task(ctx, project_id: int, task_id: int, *task_description, status: str = "incomplete"):
    try:
        task_description = " ".join(task_description)
        
        if status == "complete":
            edit_status = "complete \u2705"
        else:
            edit_status = "incomplete \u274C"

        edit(project_id, task_id, task_description, edit_status) # Edit the task in the database
        await ctx.send("Task edited!")
    except:
        await ctx.send("Task not found")

@bot.command(name="deletetask")
async def delete_task_command(ctx, project_id: int, task_id: int):
    try:
        if project_id in collection.distinct("project_id"):
            await delete_task(project_id, task_id) # Delete the task from the database
            await ctx.send("Task deleted!")
        else:
            await ctx.send("Task not found")
    except:
        await ctx.send("Error deleting task")

@bot.command(name="deleteproject")
async def delete_project_command(ctx, project_id: int):
    try:
        # Delete the project from the database
        delete_project(project_id)
        await ctx.send("Project deleted!")
    except:
        await ctx.send("Project not found")

@bot.command(name="assign")
async def assign_task(ctx, project_id: int, task_id: int, member: discord.Member):
    try:
        if project_id in collection.distinct("project_id"):
            # Store assignment in database or memory
            if project_id not in assign:
                assign[project_id] = {}
            assign[project_id][task_id] = member.id
            await ctx.send(f"{member.mention} has been assigned to task {task_id} of project {project_id}")
        else:
            await ctx.send("Project not found")
    except:
        await ctx.send("Error assigning task")

@bot.command(name="listassign")
async def list_assign(ctx, project_id: int):
    try:
        if project_id not in collection.distinct("project_id"):
            await ctx.send("No tasks found")
            return
        
        task_list = list_task(project_id)
        await ctx.send(f"Tasks for project {project_id}:\n" + "\n".join(task_list))
    except:
        await ctx.send("Please enter a valid project ID,format: /listassign **<project_id>**")
            
bot.run(BOT_TOKEN)