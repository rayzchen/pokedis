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

opts = {
    "auto_sync_commands": True,
    "loop": loop
}

if "NO_MAIN_SERVER" not in os.environ:
    from utils import main_server
    opts["debug_guilds"] = main_server

bot = AutoShardedBot(**opts)

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
