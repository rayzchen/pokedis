from keep_alive import keep_alive
import os
import sys
import threading
import importlib

t = threading.Thread(target=keep_alive, daemon=True)
t.start()

while True:
    sys.modules.pop("bot", None)
    bot = importlib.import_module("bot")
    cont = bot.run()
    if not cont:
        break

