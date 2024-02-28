import discord
from discord.ext import commands
from pymongo import MongoClient

# Replace with your MongoDB connection string and database name
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
tasks_collection = db["tasks"]
bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"


class complete(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

    @commands.slash_command(name="taskdone", description="Tag a task as done")
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
            task = tasks_collection.find_one(
                {"_id": task_id, "$set": {"server_id": server_id}}
            )
            if not task:
                await ctx.respond("Task not found", ephemeral=True)
                return
            tasks_collection.update_one({"_id": task_id}, {"_status": "done"})
            await ctx.respond(f"Task '{task['text']}' marked as done", ephemeral=True)
        except Exception as e:
            print(f"Error marking task as done: {e}")
            await ctx.respond(
                "Something went wrong marking the task as done. Please try again later.",
                ephemeral=True,
            )
