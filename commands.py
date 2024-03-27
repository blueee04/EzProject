import discord
from discord.ext import commands
from Datamodule.db import add,  list_task, edit

# MongoDB connection
from pymongo import MongoClient

client = MongoClient("mongodb+srv://hegdeadithyak:adi4720Q@prjct.0cc2j4d.mongodb.net/")
if client:
    print("Connected to the MongoDB Atlas!")
db = client["discord"]
collection = db["tasks"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"

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
    await ctx.send("Hello!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Please enter the correct format. Format: /listtask **<project_id>**")

@bot.command(name="addtask")
async def add_task(ctx, project_id: int, task_description: str,status="incomplete"):
    task_descriptions.setdefault(project_id, []).append(task_description)
    statuses.setdefault(project_id, []).append(
        {"task": task_description, "status": "incomplete \u274C"}
    )
    temp_status = "ic"
    if(status=="complete"):
        statuses[project_id][-1]["status"] = "complete \u2705"
        temp_status = "c"
    add(project_id, task_description, task_descriptions,temp_status) # Add the task to the database
    await ctx.send(f"Task added!")


@bot.command(name="listtask")
async def list_tasks(ctx, project_id: int):
    try:
        project_id = int(project_id)
        #if project id not found in the database
        if project_id not in collection.distinct("project_id"):
            await ctx.send("No tasks found")
            return
        
        task_list = list_task(project_id)
        await ctx.send(f"Tasks for project {project_id}:\n" + "\n".join(task_list))
    except :
        await ctx.send("Please enter a valid project ID,format: /listtask **<project_id>**")


@bot.command(name="edittask")
async def edit_task(ctx, project_id: int, task_id: int, status: str):
    if project_id in task_descriptions and 0 < task_id <= len(
        task_descriptions[project_id]
    ):
        
        if status == "complete":
            statuses[project_id][task_id - 1]["status"] = "complete \u2705"
        # I think else in unnecessary here but I will keep it for now
        else:
            statuses[project_id][task_id - 1]["status"] = "incomplete \u274C"
        edit(project_id, task_id,task_descriptions, collection) # Edit the task in the database
        await ctx.send("Task edited!")
    else:
        await ctx.send("Task not found")

@bot.command(name="assign")
async def assign(ctx, project_id: int, task_id: int, member: discord.Member):
    if project_id in task_descriptions and 0 < task_id <= len(
        task_descriptions[project_id]
    ):
        if member.id not in assign:
            assign[project_id][task_id] = member.id
            await ctx.send(f"{member.mention} has been assigned to task {task_id} of project {project_id}")
        else:
            ctx.send("Task already assigned")
    else:
        await ctx.send("Task not found")

@bot.command(name="listassign")
async def list_assign(ctx, project_id: int, task_id: int):
    try:
        project_id = int(project_id)
        if project_id not in collection.distinct("project_id"):
            await ctx.send("No tasks found")
            return
        
        assign_list = list_task(project_id)
        await ctx.send(f"Assignees for project tasks {project_id}:\n" + "\n".join(task_list))
    except :
        await ctx.send("Please enter a valid project ID,format: /assigntask **<project_id>**")
            
    
bot.run(bot_token)