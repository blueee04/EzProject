import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.db import set_task_deadline, get_overdue_tasks, get_tasks_due_soon, get_task_deadline, remove_task_deadline
from config.config import EMBED_COLORS

class DeadlineManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(DeadlineManagement(bot)) 