import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import EMBED_COLORS

class UtilityCommands(commands.Cog):
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

def setup(bot):
    bot.add_cog(UtilityCommands(bot)) 