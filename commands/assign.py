import discord
from discord.ext import commands
from pymongo import MongoClient

# Replace with your MongoDB connection string and database name
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
tasks_collection = db["tasks"]
bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"


class AssignBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

    @commands.slash_command(name="assigntask", description="Assign a task to a user")
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
            task = tasks_collection.find_one({"_id": task_id, "server_id": server_id})
            if not task:
                await ctx.respond("Task not found", ephemeral=True)
                return
            tasks_collection.update_one(
                {"_id": task_id}, {"$set": {"assigned_to": assign.id}}
            )
            await ctx.respond(
                f"Task '{task['text']}' assigned to {assign.display_name}",
                ephemeral=True,
            )
        except Exception as e:
            print(f"Error assigning task: {e}")
            await ctx.respond(
                "Something went wrong assigning the task. Please try again later.",
                ephemeral=True,
            )
