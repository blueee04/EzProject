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

    @commands.slash_command(name="listtask", description="List all the tasks")
    async def list_task(self, ctx, text: str, assign: discord.Member = None):
        try:
            server_id = ctx.guild.id
            tasks = tasks_collection.find({"server_id": server_id})
            tasks_text = "\n".join([f"{task['text']} - Assigned to: {task['assigned_to']}" for task in tasks])
            await ctx.respond(f"Tasks for this server:\n{tasks_text}", ephemeral=True) 
        except Exception as e:
            print(f"Error while displaying tasks: {e}")
            await ctx.respond("Error while displaying tasks", ephemeral=True)
bot = TaskBot()

# Replace with your Discord bot token
bot.run("your_bot_token")