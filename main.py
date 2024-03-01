# Bots Commands
from customcommands.startask import StartTaskBot
from customcommands.listtask import listTaskBot
from customcommands.edittask import editTaskBot
from customcommands.taskdone import complete
from customcommands.assign import AssignBot
from customcommands.addtask import Add

import discord
import numpy as np
import re


def split_string_with_space(string):
    words = re.split(r"\s+", string)
    words = [word for word in words if word]
    return words


# discord.py module
from discord.ext import commands

bot_token = "MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M"

# Bot instance
bot = commands.Bot(intents=discord.Intents.all())


# Bot event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print("------")


Tasks = {}
status = {}


@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    if message.author == bot.user:
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("!addtask"):
        msg = message.content.split("!addtask ", 1)[1]
        stuff = split_string_with_space(msg)
        proj_id = int(stuff[0])
        if proj_id not in Tasks:
            Tasks[proj_id] = []
            status[proj_id] = []

        Tasks[proj_id].append(stuff[1])
        status[proj_id].append({stuff[1]: "incomplete \u274C"})
        await message.channel.send("Task added!")

    if message.content.startswith("!listtask"):
        msg = message.content.split("!listtask ", 1)[1]
        proj_id = int(msg)
        if proj_id not in Tasks:
            await message.channel.send("No tasks found")
        else:
            a = [
                f"{i+1}. {task} - {status}"
                for i, (task, status) in enumerate(zip(Tasks[proj_id], status[proj_id]))
            ]
            await message.channel.send(
                f"List of Tasks for Project ID : {proj_id} is : \n" + "\n".join(a)
            )

    await bot.process_commands(message)


bot.run(bot_token)
