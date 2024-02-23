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

    @commands.slash_command(name="add", description="Add a new task")
    async def add_task(self, ctx, text: str, assign: discord.Member = None):
        try:
            server_id = ctx.guild.id
            task_data = {
                "text": text,
                "server_id": server_id,
                "assigned_to": assign.id if assign else None,
            }
            inserted_task = tasks_collection.insert_one(task_data)

            await ctx.respond("Task created!", ephemeral=True)
            await ctx.follow_up(f"Task '{text}' added with ID {inserted_task.inserted_id}", ephemeral=True)
        except Exception as e:
            print(f"Error adding task: {e}")
            await ctx.respond("Something went wrong adding the task. Please try again later.", ephemeral=True)

bot = TaskBot()

# Replace with your Discord bot token
bot.run("your_bot_token")