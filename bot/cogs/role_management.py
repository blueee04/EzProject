import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import EMBED_COLORS

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(RoleManagement(bot)) 