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
        bot = importlib.import_module("bot")
        cont = bot.run()
        if not cont:
            break

if __name__ == "__main__":
    main()
