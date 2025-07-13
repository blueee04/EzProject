import discord
from discord.ext import commands
from config.config import EMBED_COLORS

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