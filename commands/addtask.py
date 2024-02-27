import discord
from discord.ext import commands
from pymongo import MongoClient

# Replace with your MongoDB connection string and database name
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
tasks_collection = db["tasks"]
bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"


class TaskBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

    @commands.slash_command(name="addtask", description="Add a new task")
    async def star_task(
        self,
        ctx,
        task_id: str,
        text: str,
        server_id: str,
        _status: str,
        assign: discord.Member = None,
    ):
        try:
            server_id = ctx.guild.id
            task_data = {
                "text": text,
                "server_id": server_id,
                "assigned_to": assign.id if assign else None,
            }
            inserted_task = tasks_collection.insert_one(task_data)

            await ctx.respond("Task created!", ephemeral=True)
            await ctx.follow_up(
                f"Task '{text}' added with ID {inserted_task.inserted_id}",
                ephemeral=True,
            )
        except Exception as e:
            print(f"Error adding task: {e}")
            await ctx.respond(
                "Something went wrong adding the task. Please try again later.",
                ephemeral=True,
            )
