import os
import sys
import glob
import utils
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import discord
from discord.ext import commands
from discord_slash import SlashCommand

if os.path.isfile(".token"):
    print("Loading token")
    with open(".token") as f:
        os.environ["TOKEN"] = f.read().rstrip()

bot = commands.AutoShardedBot(command_prefix=utils.get_prefix, help_command=None, loop=loop)
slash = SlashCommand(bot, sync_commands=True)

for file in glob.glob("cogs/**/*.py", recursive=True):
    bot.load_extension(file.replace(".py", "").replace(os.path.sep, "."))

def run():
    try:
        loop.run_until_complete(bot.start(os.getenv("TOKEN")))
    except KeyboardInterrupt:
        print("Stopped")
        return False
    if os.path.isfile("stop"):
        os.remove("stop")
        return False
    return True
