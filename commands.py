import discord
from discord.ext import commands
from Datamodule.db import add,  list_task, edit, delete_task
import asyncio

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
# task_descriptions  = {}
# statuses ={}


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
        await ctx.send(f'''{ctx.author.mention} Please enter the correct format
                         \n Format:
                         \n- /addtask **<project_id>** **<task_description>** **<status>**
                         \n- /listtask **<project_id>**
                         \n- /edittask **<project_id>** **<task_id>** **<status>**''')

@bot.command(name = "helpme")
async def help(ctx):
    await ctx.send(f'''{ctx.author.mention}Commands:
                         \n Format:
                         \n- /addtask **<project_id>** **<task_description>** **<status>**
                         \n- /listtask **<project_id>**
                         \n- /edittask **<project_id>** **<task_id>** **<status>**''')

@bot.command(name="addtask")
async def add_task(ctx, project_id: int, task_description: str,status="incomplete"):
    temp_status = "ic"
    if(status=="complete"):
        temp_status = "c"
    # Add the task to the database
    add(project_id, task_description,temp_status)
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
    except :
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
    except :
        await ctx.send(f"{ctx.author.mention} Please enter a valid project ID,format: /listtask **<project_id>**")



@bot.command(name="edittask")
async def edit_task(ctx, project_id: int, task_id: int,task_description,status: str):
    try:
        if status == "complete":
            edit_status = "complete \u2705"
        
        edit_status = "incomplete \u274C"

        edit(project_id, task_id,task_description, edit_status) # Edit the task in the database
        await ctx.send("Task edited!")
    except:
        await ctx.send("Task not found")


#To be Solved Not working right now.
@bot.command(name="deletetask")
async def delete_task(ctx, project_id: int, task_id: int):
    try:
        await delete_task(project_id, task_id) # Delete the task from the database
        await ctx.send("Task deleted!")
    except:
        await ctx.send("Task not found")

@bot.command(name="deleteproject")
async def delete_project(ctx, project_id: int):
    try:
        # Delete the project from the database
        await delete_project(project_id)
        await ctx.send("Project deleted!")
    except:
        await ctx.send("Project not found")

bot.run(bot_token)