import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.db import add, list_task, edit, delete_task, delete_project
from config.config import EMBED_COLORS
from bot.utils.permissions import has_project_permission

# MongoDB connection
from pymongo import MongoClient
from config.config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

class TaskManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addtask")
    async def add_task(self, ctx, project_id: int, *task_description: str, status="incomplete"):
        task_description = " ".join(task_description)
        temp_status = "ic"
        if status == "complete":
            temp_status = "c"
        
        try:
            add(project_id, task_description, temp_status)
            
            embed = discord.Embed(
                title="✅ Task Added Successfully!",
                description=f"New task has been added to Project {project_id}",
                color=EMBED_COLORS['success']
            )
            embed.add_field(name="📋 Task Description", value=task_description, inline=False)
            embed.add_field(name="📊 Status", value="🔄 In Progress" if status == "incomplete" else "✅ Complete", inline=True)
            embed.add_field(name="🏷️ Project ID", value=project_id, inline=True)
            embed.set_footer(text=f"Added by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Adding Task",
                description=f"Failed to add task: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="listtask")
    async def list_tasks(self, ctx, project_id: int):
        try:
            if project_id not in collection.distinct("project_id"):
                embed = discord.Embed(
                    title="❌ No Tasks Found",
                    description=f"No tasks found for Project {project_id}",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            tasks = list_task(project_id)
            
            if tasks == ["No tasks found"]:
                embed = discord.Embed(
                    title="❌ No Tasks Found",
                    description=f"No tasks found for Project {project_id}",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"📋 Tasks for Project {project_id}",
                description="Here are all the tasks for this project:",
                color=EMBED_COLORS['info']
            )
            
            task_list = "\n".join(tasks)
            if len(task_list) > 1024:
                # Split into multiple fields if too long
                chunks = [task_list[i:i+1024] for i in range(0, len(task_list), 1024)]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"Tasks (Part {i+1})" if len(chunks) > 1 else "Tasks",
                        value=chunk,
                        inline=False
                    )
            else:
                embed.add_field(name="Tasks", value=task_list, inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Listing Tasks",
                description=f"Failed to list tasks: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="listall")
    async def list_all(self, ctx):
        try:
            all_projects = collection.distinct("project_id")
            
            if not all_projects:
                embed = discord.Embed(
                    title="❌ No Projects Found",
                    description="No projects have been created yet.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="📊 All Projects Overview",
                description="Here are all projects and their tasks:",
                color=EMBED_COLORS['info']
            )
            
            for project_id in all_projects:
                tasks = list_task(project_id)
                if tasks != ["No tasks found"]:
                    task_count = len(tasks)
                    embed.add_field(
                        name=f"Project {project_id} ({task_count} tasks)",
                        value="\n".join(tasks[:5]) + ("\n..." if len(tasks) > 5 else ""),
                        inline=False
                    )
            
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Listing All Projects",
                description=f"Failed to list projects: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="edittask")
    async def edit_task(self, ctx, project_id: int, task_id: int, *task_description, status: str = "incomplete"):
        task_description = " ".join(task_description)
        
        try:
            edit(project_id, task_id, task_description, status)
            
            embed = discord.Embed(
                title="✅ Task Edited Successfully!",
                description=f"Task {task_id} in Project {project_id} has been updated",
                color=EMBED_COLORS['success']
            )
            embed.add_field(name="📋 New Description", value=task_description, inline=False)
            embed.add_field(name="📊 Status", value="🔄 In Progress" if status == "incomplete" else "✅ Complete", inline=True)
            embed.set_footer(text=f"Edited by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Editing Task",
                description=f"Failed to edit task: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="deletetask")
    @has_project_permission()
    async def delete_task_command(self, ctx, project_id: int, task_id: int):
        try:
            await delete_task(project_id, task_id)
            
            embed = discord.Embed(
                title="✅ Task Deleted Successfully!",
                description=f"Task {task_id} from Project {project_id} has been deleted",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"Deleted by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Deleting Task",
                description=f"Failed to delete task: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="deleteproject")
    @has_project_permission()
    async def delete_project_command(self, ctx, project_id: int):
        try:
            delete_project(project_id)
            
            embed = discord.Embed(
                title="✅ Project Deleted Successfully!",
                description=f"Project {project_id} and all its tasks have been deleted",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"Deleted by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Deleting Project",
                description=f"Failed to delete project: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(TaskManagement(bot)) 