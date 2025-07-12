import os
import discord
from discord.ext import commands
from db.db import add, list_task, edit, delete_task, delete_project
from config.config import BOT_TOKEN, MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, EMBED_COLORS

# MongoDB connection
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store assignments in memory (you might want to move this to database later)
assignments = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Hello!")

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    help_text = f"""{interaction.user.mention} **Available Commands:**
    
**Task Management:**
• `/addtask` - Add a new task to a project
• `/listtask` - List all tasks in a project
• `/listall` - List all projects and their tasks
• `/edittask` - Edit an existing task
• `/deletetask` - Delete a specific task
• `/deleteproject` - Delete an entire project

**Assignment:**
• `/assign` - Assign a member to a task
• `/listassign` - List assignments for a project

**Utility:**
• `/hello` - Say hello to the bot
• `/help` - Show this help message"""
    
    await interaction.response.send_message(help_text)

@bot.tree.command(name="addtask", description="Add a new task to a project")
async def add_task(interaction: discord.Interaction, project_id: int, task_description: str, status: str = "incomplete"):
    try:
        temp_status = "ic"
        if status == "complete":
            temp_status = "c"
        
        add(project_id, task_description, temp_status)
        await interaction.response.send_message(f"{interaction.user.mention} Task added to project {project_id}!")
    except Exception as e:
        await interaction.response.send_message(f"Error adding task: {str(e)}", ephemeral=True)

@bot.tree.command(name="listtask", description="List all tasks in a project")
async def list_tasks(interaction: discord.Interaction, project_id: int):
    try:
        if project_id not in collection.distinct("project_id"):
            await interaction.response.send_message("No tasks found for this project ID", ephemeral=True)
            return
        
        task_list = list_task(project_id)
        embed = discord.Embed(
            title=f"Tasks for Project {project_id}",
            description="\n".join(task_list),
            color=EMBED_COLORS['info']
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error listing tasks: {str(e)}", ephemeral=True)

@bot.tree.command(name="listall", description="List all projects and their tasks")
async def list_all(interaction: discord.Interaction):
    try:
        project_ids = collection.distinct("project_id")
        if len(project_ids) == 0:
            await interaction.response.send_message("No projects found", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="All Projects and Tasks",
            color=EMBED_COLORS['success']
        )
        
        for project_id in project_ids:
            task_list = list_task(project_id)
            embed.add_field(
                name=f"Project {project_id}",
                value="\n".join(task_list) if task_list else "No tasks",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error listing all projects: {str(e)}", ephemeral=True)

@bot.tree.command(name="edittask", description="Edit an existing task")
async def edit_task(interaction: discord.Interaction, project_id: int, task_id: int, task_description: str, status: str = "incomplete"):
    try:
        if status == "complete":
            edit_status = "complete \u2705"
        else:
            edit_status = "incomplete \u274C"
        
        edit(project_id, task_id, task_description, edit_status)
        await interaction.response.send_message(f"{interaction.user.mention} Task {task_id} in project {project_id} has been edited!")
    except Exception as e:
        await interaction.response.send_message(f"Error editing task: {str(e)}", ephemeral=True)

@bot.tree.command(name="deletetask", description="Delete a specific task")
async def delete_task_command(interaction: discord.Interaction, project_id: int, task_id: int):
    try:
        if project_id in collection.distinct("project_id"):
            await delete_task(project_id, task_id)
            await interaction.response.send_message(f"{interaction.user.mention} Task {task_id} in project {project_id} has been deleted!")
        else:
            await interaction.response.send_message("Project not found", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error deleting task: {str(e)}", ephemeral=True)

@bot.tree.command(name="deleteproject", description="Delete an entire project")
async def delete_project_command(interaction: discord.Interaction, project_id: int):
    try:
        delete_project(project_id)
        await interaction.response.send_message(f"{interaction.user.mention} Project {project_id} has been deleted!")
    except Exception as e:
        await interaction.response.send_message(f"Error deleting project: {str(e)}", ephemeral=True)

@bot.tree.command(name="assign", description="Assign a member to a task")
async def assign_task(interaction: discord.Interaction, project_id: int, task_id: int, member: discord.Member):
    try:
        if project_id in collection.distinct("project_id"):
            if project_id not in assignments:
                assignments[project_id] = {}
            assignments[project_id][task_id] = member.id
            await interaction.response.send_message(f"{member.mention} has been assigned to task {task_id} of project {project_id}!")
        else:
            await interaction.response.send_message("Project not found", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error assigning task: {str(e)}", ephemeral=True)

@bot.tree.command(name="listassign", description="List assignments for a project")
async def list_assign(interaction: discord.Interaction, project_id: int):
    try:
        if project_id not in collection.distinct("project_id"):
            await interaction.response.send_message("No tasks found for this project", ephemeral=True)
            return
        
        task_list = list_task(project_id)
        embed = discord.Embed(
            title=f"Tasks and Assignments for Project {project_id}",
            color=EMBED_COLORS['purple']
        )
        
        for task in task_list:
            task_id = task.split('.')[0]
            if project_id in assignments and int(task_id) in assignments[project_id]:
                member_id = assignments[project_id][int(task_id)]
                member = interaction.guild.get_member(member_id)
                assignee = member.mention if member else f"<@{member_id}>"
                embed.add_field(name=task, value=f"Assigned to: {assignee}", inline=False)
            else:
                embed.add_field(name=task, value="Unassigned", inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error listing assignments: {str(e)}", ephemeral=True)

@bot.tree.command(name="status", description="Update task status")
async def update_status(interaction: discord.Interaction, project_id: int, task_id: int, status: str):
    try:
        # Get current task description
        task = collection.find_one({"project_id": project_id, "task_id": task_id})
        if not task:
            await interaction.response.send_message("Task not found", ephemeral=True)
            return
        
        task_description = task["description"]
        
        if status == "complete":
            edit_status = "complete \u2705"
        else:
            edit_status = "incomplete \u274C"
        
        edit(project_id, task_id, task_description, edit_status)
        await interaction.response.send_message(f"{interaction.user.mention} Task {task_id} status updated to {status}!")
    except Exception as e:
        await interaction.response.send_message(f"Error updating status: {str(e)}", ephemeral=True)

def main():
    """Main function to run the bot"""
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Error running bot: {e}")

if __name__ == "__main__":
    main() 