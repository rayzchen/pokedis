import os
import sys
import glob
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from discord import AutoShardedBot # upm packge(pycord)

if os.path.isfile(".token"):
    print("Loading token")
    with open(".token") as f:
        os.environ["TOKEN"] = f.read().rstrip()

bot = AutoShardedBot(debug_guilds=[894254591858851871],
                     auto_sync_commands=True,
                     loop=loop)

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
