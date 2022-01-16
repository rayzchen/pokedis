from traceback import print_exc
from server import keep_alive
import sys
import threading
import importlib

def reset_modules():
    pending = []
    for module in sys.modules:
        if module.startswith("utils") or module.startswith("cogs") or module == "bot":
            pending.append(module)
    for mod in pending:
        sys.modules.pop(mod)

def main():
    t = threading.Thread(target=keep_alive)
    t.daemon = True
    t.start()

    while True:
        reset_modules()
        try:
            bot = importlib.import_module("bot")
            cont = bot.run()
            if not cont:
                break
        except Exception as e:
            print_exc(e)
            continue

if __name__ == "__main__":
    main()
