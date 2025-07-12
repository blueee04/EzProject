import discord
from discord.ext import commands
from db.db import add, list_task, edit, delete_task, delete_project, assign_task_to_user, get_task_assignment, get_project_assignments, remove_task_assignment, set_task_deadline, get_overdue_tasks, get_tasks_due_soon, get_task_deadline, remove_task_deadline
import asyncio
from config.config import BOT_TOKEN, MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, EMBED_COLORS

# MongoDB connection
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
if client:
    print("Connected to the MongoDB Atlas!")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

intents = discord.Intents.default()
# Remove message_content for older discord.py versions
# intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Remove the default help command to avoid conflicts
bot.remove_command('help')

# Permission check function
def has_project_permission():
    async def predicate(ctx):
        # Check if user has Project Manager role or is admin
        project_manager_role = discord.utils.get(ctx.guild.roles, name="Project Manager")
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        
        if project_manager_role and project_manager_role in ctx.author.roles:
            return True
        if admin_role and admin_role in ctx.author.roles:
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need the 'Project Manager' role or admin permissions to use this command.",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
        return False
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")

@bot.command(name="hello")
async def hello(ctx):
    embed = discord.Embed(
        title="👋 Hello!",
        description=f"Welcome {ctx.author.mention}! I'm your project management assistant.",
        color=EMBED_COLORS['info']
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if ctx.command and ctx.command.name == "helpme":
        return  # Prevent double response for helpme command
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Command Error",
            description=f"{ctx.author.mention} Please enter the correct format",
            color=EMBED_COLORS['error']
        )
        embed.add_field(
            name="📋 Available Formats",
            value="""
            • `/addtask` **<project_id>** **<task_description>** **<status>**
            • `/listtask` **<project_id>**
            • `/edittask` **<project_id>** **<task_id>** **<new_task>** **<status>**
            • `/listall` - List all projects
            • `/deletetask` **<project_id>** **<task_id>** *(Project Manager only)*
            • `/deleteproject` **<project_id>** *(Project Manager only)*
            • `/assign` **<project_id>** **<task_id>** **<member>**
            • `/unassign` **<project_id>** **<task_id>**
            • `/deadline` **<project_id>** **<task_id>** **<YYYY-MM-DD>**
            • `/overdue` - Show overdue tasks
            • `/duesoon` - Show tasks due soon
            """,
            inline=False
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="helpme")
async def helpme(ctx):
    embed = discord.Embed(
        title="EzProject Bot Commands",
        description="Here are all the available commands for project management:",
        color=EMBED_COLORS['info']
    )
    
    embed.add_field(
        name="📝 Task Management",
        value="""
        • `/addtask` - Add a new task to a project
        • `/listtask` - List all tasks in a project
        • `/listall` - List all projects and their tasks
        • `/edittask` - Edit an existing task
        • `/deletetask` - Delete a specific task *(Project Manager only)*
        • `/deleteproject` - Delete an entire project *(Project Manager only)*
        """,
        inline=False
    )
    
    embed.add_field(
        name="👥 Assignment Management",
        value="""
        • `/assign` - Assign a member to a task
        • `/unassign` - Remove assignment from a task
        • `/listassign` - List assignments for a project
        """,
        inline=False
    )
    
    embed.add_field(
        name="⏰ Deadline Management",
        value="""
        • `/deadline` - Set a deadline for a task
        • `/overdue` - Show overdue tasks
        • `/duesoon` - Show tasks due soon
        """,
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Utility",
        value="""
        • `/hello` - Say hello to the bot
        • `/helpme` - Show this help message
        • `/ping` - Check bot latency
        """,
        inline=False
    )
    
    embed.add_field(
        name="🔐 Permissions",
        value="""
        • **Project Manager** role required for deleting tasks/projects
        • **Admin** role or server admin can use all commands
        • Contact server admin to get appropriate roles
        """,
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="addtask")
async def add_task(ctx, project_id: int, *task_description: str, status="incomplete"):
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

@bot.command(name="listtask")
async def list_tasks(ctx, project_id: int):
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
        
        task_list = list_task(project_id)
        
        embed = discord.Embed(
            title=f"📋 Tasks for Project {project_id}",
            description="Here are all the tasks in this project:",
            color=EMBED_COLORS['info']
        )
        
        if task_list and task_list[0] != "No tasks found":
            for task in task_list:
                # Extract task info
                parts = task.split('. ', 1)
                if len(parts) == 2:
                    task_id = parts[0]
                    task_info = parts[1]
                    
                    # Determine status and emoji
                    if "✅" in task_info:
                        status_emoji = "✅"
                        status_text = "Complete"
                    else:
                        status_emoji = "🔄"
                        status_text = "In Progress"
                    
                    # Check assignment
                    assignment = get_task_assignment(project_id, int(task_id))
                    if assignment:
                        member = ctx.guild.get_member(assignment)
                        assignee = member.mention if member else f"<@{assignment}>"
                        task_info += f"\n👤 **Assigned to:** {assignee}"
                    
                    embed.add_field(
                        name=f"Task {task_id}",
                        value=f"{task_info}\n**Status:** {status_emoji} {status_text}",
                        inline=False
                    )
        else:
            embed.add_field(name="No Tasks", value="This project has no tasks yet.", inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Error listing tasks: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="listall")
async def list_all(ctx):
    try:
        if len(collection.distinct("project_id")) == 0:
            embed = discord.Embed(
                title="❌ No Projects Found",
                description="There are no projects in the database yet.",
                color=EMBED_COLORS['warning']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 All Projects Overview",
            description="Here are all projects and their tasks:",
            color=EMBED_COLORS['success']
        )
        
        for project_id in collection.distinct("project_id"):
            task_list = list_task(project_id)
            
            if task_list and task_list[0] != "No tasks found":
                # Count tasks by status
                total_tasks = len(task_list)
                completed_tasks = sum(1 for task in task_list if "✅" in task)
                progress = f"{completed_tasks}/{total_tasks} completed"
                
                embed.add_field(
                    name=f"🏷️ Project {project_id}",
                    value=f"**Progress:** {progress}\n**Tasks:** {total_tasks}",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"🏷️ Project {project_id}",
                    value="**Progress:** 0/0 completed\n**Tasks:** 0",
                    inline=True
                )
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Error listing all projects: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="edittask")
async def edit_task(ctx, project_id: int, task_id: int, *task_description, status: str = "incomplete"):
    try:
        task_description = " ".join(task_description)
        
        if status == "complete":
            edit_status = "complete \u2705"
        else:
            edit_status = "incomplete \u274C"

        edit(project_id, task_id, task_description, edit_status)
        
        embed = discord.Embed(
            title="✏️ Task Edited Successfully!",
            description=f"Task {task_id} in Project {project_id} has been updated",
            color=EMBED_COLORS['success']
        )
        embed.add_field(name="📋 New Description", value=task_description, inline=False)
        embed.add_field(name="📊 New Status", value="✅ Complete" if status == "complete" else "🔄 In Progress", inline=True)
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

@bot.command(name="deletetask")
@has_project_permission()
async def delete_task_command(ctx, project_id: int, task_id: int):
    try:
        if project_id in collection.distinct("project_id"):
            await delete_task(project_id, task_id)
            
            embed = discord.Embed(
                title="🗑️ Task Deleted Successfully!",
                description=f"Task {task_id} in Project {project_id} has been deleted",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"Deleted by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project {project_id} does not exist",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Deleting Task",
            description=f"Failed to delete task: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="deleteproject")
@has_project_permission()
async def delete_project_command(ctx, project_id: int):
    try:
        delete_project(project_id)
        
        embed = discord.Embed(
            title="🗑️ Project Deleted Successfully!",
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

@bot.command(name="assign")
async def assign_task(ctx, project_id: int, task_id: int, member: discord.Member):
    try:
        if project_id in collection.distinct("project_id"):
            success = assign_task_to_user(project_id, task_id, member.id)
            
            if success:
                embed = discord.Embed(
                    title="👥 Task Assigned Successfully!",
                    description=f"{member.mention} has been assigned to task {task_id} of project {project_id}",
                    color=EMBED_COLORS['success']
                )
                embed.add_field(name="👤 Assigned To", value=member.mention, inline=True)
                embed.add_field(name="📋 Task ID", value=task_id, inline=True)
                embed.add_field(name="🏷️ Project ID", value=project_id, inline=True)
                embed.set_footer(text=f"Assigned by {ctx.author.name}")
                
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Task Not Found",
                    description=f"Task {task_id} in Project {project_id} does not exist",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project {project_id} does not exist",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Assigning Task",
            description=f"Failed to assign task: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="unassign")
async def unassign_task(ctx, project_id: int, task_id: int):
    try:
        if project_id in collection.distinct("project_id"):
            success = remove_task_assignment(project_id, task_id)
            
            if success:
                embed = discord.Embed(
                    title="👤 Task Unassigned Successfully!",
                    description=f"Assignment removed from task {task_id} in project {project_id}",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Unassigned by {ctx.author.name}")
                
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Task Not Found",
                    description=f"Task {task_id} in Project {project_id} does not exist",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project {project_id} does not exist",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Unassigning Task",
            description=f"Failed to unassign task: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="listassign")
async def list_assign(ctx, project_id: int):
    try:
        if project_id not in collection.distinct("project_id"):
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project {project_id} does not exist",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            return
        
        task_list = list_task(project_id)
        assignments = get_project_assignments(project_id)
        
        embed = discord.Embed(
            title=f"👥 Assignments for Project {project_id}",
            description="Here are all tasks and their assignments:",
            color=EMBED_COLORS['purple']
        )
        
        for task in task_list:
            task_id = task.split('.')[0]
            if int(task_id) in assignments:
                member_id = assignments[int(task_id)]
                member = ctx.guild.get_member(member_id)
                assignee = member.mention if member else f"<@{member_id}>"
                embed.add_field(name=task, value=f"👤 **Assigned to:** {assignee}", inline=False)
            else:
                embed.add_field(name=task, value="👤 **Assigned to:** Unassigned", inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Listing Assignments",
            description=f"Failed to list assignments: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="deadline")
async def set_deadline(ctx, project_id: int, task_id: int, deadline: str):
    try:
        if project_id in collection.distinct("project_id"):
            success = set_task_deadline(project_id, task_id, deadline)
            
            if success:
                embed = discord.Embed(
                    title="⏰ Deadline Set Successfully!",
                    description=f"Deadline set for task {task_id} in project {project_id}",
                    color=EMBED_COLORS['success']
                )
                embed.add_field(name="📅 Deadline", value=deadline, inline=True)
                embed.add_field(name="📋 Task ID", value=task_id, inline=True)
                embed.add_field(name="🏷️ Project ID", value=project_id, inline=True)
                embed.set_footer(text=f"Set by {ctx.author.name}")
                
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="❌ Task Not Found",
                    description=f"Task {task_id} in Project {project_id} does not exist",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Project Not Found",
                description=f"Project {project_id} does not exist",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Setting Deadline",
            description=f"Failed to set deadline: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="overdue")
async def show_overdue(ctx):
    try:
        overdue_tasks = get_overdue_tasks()
        
        if not overdue_tasks:
            embed = discord.Embed(
                title="✅ No Overdue Tasks",
                description="Great job! All tasks are up to date.",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="⚠️ Overdue Tasks",
            description="These tasks are past their deadline:",
            color=EMBED_COLORS['warning']
        )
        
        for task in overdue_tasks:
            task_info = f"**Project {task['project_id']}, Task {task['task_id']}**\n"
            task_info += f"📋 {task['description']}\n"
            task_info += f"📅 Due: {task['deadline']}"
            
            if "assigned_to" in task:
                member = ctx.guild.get_member(task["assigned_to"])
                assignee = member.mention if member else f"<@{task['assigned_to']}>"
                task_info += f"\n👤 Assigned to: {assignee}"
            
            embed.add_field(name=f"⚠️ Overdue", value=task_info, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Getting Overdue Tasks",
            description=f"Failed to get overdue tasks: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="duesoon")
async def show_due_soon(ctx, days: int = 3):
    try:
        due_soon_tasks = get_tasks_due_soon(days)
        
        if not due_soon_tasks:
            embed = discord.Embed(
                title="📅 No Tasks Due Soon",
                description=f"No tasks are due in the next {days} days.",
                color=EMBED_COLORS['info']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📅 Tasks Due in Next {days} Days",
            description="These tasks are approaching their deadline:",
            color=EMBED_COLORS['info']
        )
        
        for task in due_soon_tasks:
            task_info = f"**Project {task['project_id']}, Task {task['task_id']}**\n"
            task_info += f"📋 {task['description']}\n"
            task_info += f"📅 Due: {task['deadline']}"
            
            if "assigned_to" in task:
                member = ctx.guild.get_member(task["assigned_to"])
                assignee = member.mention if member else f"<@{task['assigned_to']}>"
                task_info += f"\n👤 Assigned to: {assignee}"
            
            embed.add_field(name=f"⏰ Due Soon", value=task_info, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error Getting Tasks Due Soon",
            description=f"Failed to get tasks due soon: {str(e)}",
            color=EMBED_COLORS['error']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{round(bot.latency * 1000)}ms**",
        color=EMBED_COLORS['info']
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)
            
bot.run(BOT_TOKEN)