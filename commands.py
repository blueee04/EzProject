bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

task_descriptions = {}
statuses = {}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")


@bot.slash_command(name="hello")
async def hello(ctx):
    await ctx.send("Hello!")


@bot.slash_command(name="addtask")
async def add_task(ctx, project_id: int, task_description: str):
    task_descriptions.setdefault(project_id, []).append(task_description)
    statuses.setdefault(project_id, []).append(
        {"task": task_description, "status": "incomplete \u274C"}
    )
    await ctx.send(f"Task added!")


@bot.slash_command(name="listtask")
async def list_tasks(ctx, project_id: int):
    if project_id not in task_descriptions:
        await ctx.send("No tasks found")
    else:
        task_list = [
            f"{i+1}. {task['task']} - {task['status']} "
            for i, task in enumerate(statuses[project_id])
        ]
        await ctx.send(
            f"List of Tasks for Project ID : {project_id} is : \n"
            + "\n".join(task_list)
        )


@bot.slash_command(name="edittask")
async def edit_task(ctx, project_id: int, task_id: int, new_description: str):
    if project_id in task_descriptions and 0 < task_id <= len(
        task_descriptions[project_id]
    ):
        task_descriptions[project_id][task_id - 1] = new_description
        statuses[project_id][task_id - 1]["task"] = new_description
        await ctx.send("Task edited!")
    else:
        await ctx.send("Task not found")


bot.run(bot_token)
