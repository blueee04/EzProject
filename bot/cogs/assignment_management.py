import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.db import assign_task_to_user, get_task_assignment, get_project_assignments, remove_task_assignment
from config.config import EMBED_COLORS

class AssignmentManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(AssignmentManagement(bot)) 