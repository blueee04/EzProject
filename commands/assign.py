import discord
from discord.ext import commands
from pymongo import MongoClient

# Replace with your MongoDB connection string and database name
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
tasks_collection = db["tasks"]

class TaskBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

    @commands.slash_command(name="assigntask", description="Assign a task to a user")
    async def assign_task(self, ctx, task_id: str, assign: discord.Member):
        try:
            server_id = ctx.guild.id
            task = tasks_collection.find_one({"_id": task_id, "server_id": server_id})
            if not task:
                await ctx.respond("Task not found", ephemeral=True)
                return
            tasks_collection.update_one({"_id": task_id}, {"$set": {"assigned_to": assign.id}})
            await ctx.respond(f"Task '{task['text']}' assigned to {assign.display_name}", ephemeral=True)
        except Exception as e:
            print(f"Error assigning task: {e}")
            await ctx.respond("Something went wrong assigning the task. Please try again later.", ephemeral=True)
bot = TaskBot()

# Replace with your Discord bot token
bot.run("your_bot_token")