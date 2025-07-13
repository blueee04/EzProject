import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to the path so we can import config and db modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import BOT_TOKEN, COMMAND_PREFIX, EMBED_COLORS

# Bot instance with proper intents
intents = discord.Intents.default()
# intents.message_content = True  # Not available in discord.py v1.x
intents.members = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📊 Connected to {len(bot.guilds)} guild(s)")
    print("🚀 Bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"Command `{ctx.message.content.split()[0]}` not found.\nUse `{COMMAND_PREFIX}helpme` to see available commands.",
            color=EMBED_COLORS['error']
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: {error.param.name}",
            color=EMBED_COLORS['error']
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(error)}",
            color=EMBED_COLORS['error']
        )
        await ctx.send(embed=embed)

# Load all cogs

def load_cogs():
    """Load all command cogs"""
    try:
        bot.load_extension("bot.cogs.task_management")
        bot.load_extension("bot.cogs.assignment_management")
        bot.load_extension("bot.cogs.deadline_management")
        bot.load_extension("bot.cogs.role_management")
        bot.load_extension("bot.cogs.utility_commands")
        print("✅ All cogs loaded successfully")
    except Exception as e:
        print(f"❌ Error loading cogs: {e}")

# Run the bot
if __name__ == "__main__":
    load_cogs()
    bot.run(BOT_TOKEN)
