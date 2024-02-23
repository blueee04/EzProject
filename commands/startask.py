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

    @commands.slash_command(name="startask", description="Edit task status")
    async def update_task(self, ctx, task_id: str, text: str, assign: discord.Member = None):
        try:
            server_id = ctx.guild.id
            task = tasks_collection.find_one({"_id": task_id, "server_id": server_id})
            if not task:
                await ctx.respond("Task not found", ephemeral=True)
                return
            tasks_collection.update_one({"_id": task_id}, {"_status": "in_progress"})
            await ctx.respond(f"Task '{task['text']}' started", ephemeral=True)
        except Exception as e:
            print(f"Error starting task: {e}")
            await ctx.respond("Something went wrong starting the task. Please try again later.", ephemeral=True)
bot = TaskBot()

# Replace with your Discord bot token
bot.run("your_bot_token")
            