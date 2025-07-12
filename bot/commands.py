import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class ProjectCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx):
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Welcome {ctx.author.mention}! I'm your project management assistant.",
            color=EMBED_COLORS['info']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name="helpme")
    async def helpme(self, ctx):
        embed = discord.Embed(
            title="EzProject Bot Commands",
            description="Here are all the available commands for project management:",
            color=EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="📝 Task Management",
            value="""
            **!addtask** `<project_id>` `<task_description>` [status]
            • Example: `!addtask 1 Create user interface complete`
            
            **!listtask** `<project_id>`
            • Example: `!listtask 1`
            
            **!listall**
            • Example: `!listall`
            
            **!edittask** `<project_id>` `<task_id>` `<new_description>` [status]
            • Example: `!edittask 1 2 Update user interface incomplete`
            
            **!deletetask** `<project_id>` `<task_id>` *(Project Manager only)*
            • Example: `!deletetask 1 2`
            
            **!deleteproject** `<project_id>` *(Project Manager only)*
            • Example: `!deleteproject 1`
            """,
            inline=False
        )
        
        embed.add_field(
            name="👥 Assignment Management",
            value="""
            **!assign** `<project_id>` `<task_id>` `<@user>`
            • Example: `!assign 1 2 @username`
            
            **!unassign** `<project_id>` `<task_id>`
            • Example: `!unassign 1 2`
            
            **!listassign** `<project_id>`
            • Example: `!listassign 1`
            """,
            inline=False
        )
        
        embed.add_field(
            name="⏰ Deadline Management",
            value="""
            **!deadline** `<project_id>` `<task_id>` `<YYYY-MM-DD>`
            • Example: `!deadline 1 2 2024-12-31`
            
            **!overdue**
            • Example: `!overdue`
            
            **!duesoon** [days]
            • Example: `!duesoon` or `!duesoon 7`
            """,
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Role Management *(Admin only)*",
            value="""
            **!createrole** `<role_name>`
            • Example: `!createrole Project Manager`
            
            **!giverole** `<@user>` `<role_name>`
            • Example: `!giverole @username Project Manager`
            
            **!removerole** `<@user>` `<role_name>`
            • Example: `!removerole @username Project Manager`
            
            **!deleterole** `<role_name>`
            • Example: `!deleterole Test Role`
            
            **!listroles**
            • Example: `!listroles`
            
            **!myroles** [@user]
            • Example: `!myroles` or `!myroles @username`
            """,
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Utility",
            value="""
            **!hello**
            • Example: `!hello`
            
            **!helpme**
            • Example: `!helpme`
            
            **!ping**
            • Example: `!ping`
            """,
            inline=False
        )
        
        embed.add_field(
            name="📋 Format Guide",
            value="""
            • `<required>` - Required parameter
            • `[optional]` - Optional parameter
            • `@username` - Mention a user
            • `YYYY-MM-DD` - Date format (e.g., 2024-12-31)
            • Status options: `complete` or `incomplete`
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

    @commands.command(name="assign")
    async def assign_task(self, ctx, project_id: int, task_id: int, member: discord.Member):
        try:
            success = assign_task_to_user(project_id, task_id, member.id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Task Assigned Successfully!",
                    description=f"Task {task_id} in Project {project_id} has been assigned to {member.mention}",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Assigned by {ctx.author.name}")
            else:
                embed = discord.Embed(
                    title="❌ Assignment Failed",
                    description=f"Task {task_id} in Project {project_id} not found",
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

    @commands.command(name="unassign")
    async def unassign_task(self, ctx, project_id: int, task_id: int):
        try:
            success = remove_task_assignment(project_id, task_id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Task Unassigned Successfully!",
                    description=f"Assignment removed from Task {task_id} in Project {project_id}",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Unassigned by {ctx.author.name}")
            else:
                embed = discord.Embed(
                    title="❌ Unassignment Failed",
                    description=f"Task {task_id} in Project {project_id} not found or not assigned",
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

    @commands.command(name="listassign")
    async def list_assign(self, ctx, project_id: int):
        try:
            assignments = get_project_assignments(project_id)
            
            if not assignments:
                embed = discord.Embed(
                    title="❌ No Assignments Found",
                    description=f"No assignments found for Project {project_id}",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"👥 Assignments for Project {project_id}",
                description="Here are all task assignments for this project:",
                color=EMBED_COLORS['info']
            )
            
            for task_id, user_id in assignments.items():
                member = ctx.guild.get_member(user_id)
                member_name = member.mention if member else f"User {user_id}"
                embed.add_field(
                    name=f"Task {task_id}",
                    value=f"Assigned to: {member_name}",
                    inline=True
                )
            
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

    @commands.command(name="deadline")
    async def set_deadline(self, ctx, project_id: int, task_id: int, deadline: str):
        try:
            success = set_task_deadline(project_id, task_id, deadline)
            
            if success:
                embed = discord.Embed(
                    title="✅ Deadline Set Successfully!",
                    description=f"Deadline for Task {task_id} in Project {project_id} has been set to {deadline}",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Set by {ctx.author.name}")
            else:
                embed = discord.Embed(
                    title="❌ Setting Deadline Failed",
                    description=f"Task {task_id} in Project {project_id} not found",
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

    @commands.command(name="overdue")
    async def show_overdue(self, ctx):
        try:
            overdue_tasks = get_overdue_tasks()
            
            if not overdue_tasks:
                embed = discord.Embed(
                    title="✅ No Overdue Tasks",
                    description="All tasks are up to date!",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="⚠️ Overdue Tasks",
                description="Here are all overdue tasks:",
                color=EMBED_COLORS['warning']
            )
            
            for task in overdue_tasks:
                task_info = f"Project {task['project_id']}, Task {task['task_id']}: {task['description']}"
                if len(task_info) > 1024:
                    task_info = task_info[:1021] + "..."
                embed.add_field(
                    name=f"Overdue Task",
                    value=task_info,
                    inline=False
                )
            
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

    @commands.command(name="duesoon")
    async def show_due_soon(self, ctx, days: int = 3):
        try:
            due_soon_tasks = get_tasks_due_soon(days)
            
            if not due_soon_tasks:
                embed = discord.Embed(
                    title="✅ No Tasks Due Soon",
                    description=f"No tasks are due within the next {days} days",
                    color=EMBED_COLORS['success']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"⏰ Tasks Due Within {days} Days",
                description="Here are tasks due soon:",
                color=EMBED_COLORS['warning']
            )
            
            for task in due_soon_tasks:
                task_info = f"Project {task['project_id']}, Task {task['task_id']}: {task['description']} (Due: {task['deadline']})"
                if len(task_info) > 1024:
                    task_info = task_info[:1021] + "..."
                embed.add_field(
                    name=f"Due Soon Task",
                    value=task_info,
                    inline=False
                )
            
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

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=EMBED_COLORS['info']
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    # Role Management Commands
    @commands.command(name="createrole")
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx, role_name: str):
        """Create a new role in the server"""
        try:
            # Check if role already exists
            existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
            if existing_role:
                embed = discord.Embed(
                    title="❌ Role Already Exists",
                    description=f"Role '{role_name}' already exists in this server.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Create the new role
            new_role = await ctx.guild.create_role(name=role_name)
            
            embed = discord.Embed(
                title="✅ Role Created Successfully!",
                description=f"Role '{role_name}' has been created.",
                color=EMBED_COLORS['success']
            )
            embed.add_field(name="🏷️ Role Name", value=role_name, inline=True)
            embed.add_field(name="🆔 Role ID", value=new_role.id, inline=True)
            embed.set_footer(text=f"Created by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Creating Role",
                description=f"Failed to create role: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="giverole")
    @commands.has_permissions(administrator=True)
    async def give_role(self, ctx, member: discord.Member, role_name: str):
        """Assign a role to a user"""
        try:
            # Find the role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description=f"Role '{role_name}' does not exist in this server.",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Check if user already has the role
            if role in member.roles:
                embed = discord.Embed(
                    title="❌ User Already Has Role",
                    description=f"{member.mention} already has the '{role_name}' role.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Assign the role
            await member.add_roles(role)
            
            embed = discord.Embed(
                title="✅ Role Assigned Successfully!",
                description=f"Role '{role_name}' has been assigned to {member.mention}",
                color=EMBED_COLORS['success']
            )
            embed.add_field(name="👤 User", value=member.mention, inline=True)
            embed.add_field(name="🏷️ Role", value=role_name, inline=True)
            embed.set_footer(text=f"Assigned by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Assigning Role",
                description=f"Failed to assign role: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="removerole")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, member: discord.Member, role_name: str):
        """Remove a role from a user"""
        try:
            # Find the role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description=f"Role '{role_name}' does not exist in this server.",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Check if user has the role
            if role not in member.roles:
                embed = discord.Embed(
                    title="❌ User Doesn't Have Role",
                    description=f"{member.mention} doesn't have the '{role_name}' role.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Remove the role
            await member.remove_roles(role)
            
            embed = discord.Embed(
                title="✅ Role Removed Successfully!",
                description=f"Role '{role_name}' has been removed from {member.mention}",
                color=EMBED_COLORS['success']
            )
            embed.add_field(name="👤 User", value=member.mention, inline=True)
            embed.add_field(name="🏷️ Role", value=role_name, inline=True)
            embed.set_footer(text=f"Removed by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Removing Role",
                description=f"Failed to remove role: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="listroles")
    async def list_roles(self, ctx):
        """List all roles in the server"""
        try:
            roles = ctx.guild.roles[1:]  # Skip @everyone role
            
            if not roles:
                embed = discord.Embed(
                    title="❌ No Roles Found",
                    description="This server has no custom roles.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"🏷️ Roles in {ctx.guild.name}",
                description="Here are all the roles in this server:",
                color=EMBED_COLORS['info']
            )
            
            # Group roles by color for better organization
            role_list = []
            for role in roles:
                member_count = len(role.members)
                role_info = f"• {role.mention} ({member_count} members)"
                role_list.append(role_info)
            
            role_text = "\n".join(role_list)
            if len(role_text) > 1024:
                # Split into multiple fields if too long
                chunks = [role_text[i:i+1024] for i in range(0, len(role_text), 1024)]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"Roles (Part {i+1})" if len(chunks) > 1 else "Roles",
                        value=chunk,
                        inline=False
                    )
            else:
                embed.add_field(name="Roles", value=role_text, inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Listing Roles",
                description=f"Failed to list roles: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="myroles")
    async def my_roles(self, ctx, member: discord.Member = None):
        """Show roles for yourself or another user"""
        try:
            # If no member specified, use the command author
            if member is None:
                member = ctx.author
            
            roles = [role for role in member.roles if role.name != "@everyone"]
            
            if not roles:
                embed = discord.Embed(
                    title="❌ No Roles Found",
                    description=f"{member.mention} has no custom roles.",
                    color=EMBED_COLORS['warning']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"🏷️ Roles for {member.display_name}",
                description=f"Here are all the roles for {member.mention}:",
                color=EMBED_COLORS['info']
            )
            
            role_list = []
            for role in roles:
                role_info = f"• {role.mention}"
                role_list.append(role_info)
            
            role_text = "\n".join(role_list)
            if len(role_text) > 1024:
                # Split into multiple fields if too long
                chunks = [role_text[i:i+1024] for i in range(0, len(role_text), 1024)]
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"Roles (Part {i+1})" if len(chunks) > 1 else "Roles",
                        value=chunk,
                        inline=False
                    )
            else:
                embed.add_field(name="Roles", value=role_text, inline=False)
            
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Getting Roles",
                description=f"Failed to get roles: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    @commands.command(name="deleterole")
    @commands.has_permissions(administrator=True)
    async def delete_role(self, ctx, role_name: str):
        """Delete a role from the server"""
        try:
            # Find the role
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="❌ Role Not Found",
                    description=f"Role '{role_name}' does not exist in this server.",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Check if it's a managed role (bot role)
            if role.managed:
                embed = discord.Embed(
                    title="❌ Cannot Delete Managed Role",
                    description=f"Role '{role_name}' is managed by a bot and cannot be deleted.",
                    color=EMBED_COLORS['error']
                )
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                return

            # Delete the role
            await role.delete()
            
            embed = discord.Embed(
                title="✅ Role Deleted Successfully!",
                description=f"Role '{role_name}' has been deleted from the server.",
                color=EMBED_COLORS['success']
            )
            embed.set_footer(text=f"Deleted by {ctx.author.name}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Deleting Role",
                description=f"Failed to delete role: {str(e)}",
                color=EMBED_COLORS['error']
            )
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProjectCommands(bot))