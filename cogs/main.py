from discord.ext import commands, tasks
from discord_slash import SlashContext
import os
from utils import send_embed

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready")
        print("Logged in as:", self.bot.user)
        print("ID:", self.bot.user.id)
        self.restart_checker.start()

    @tasks.loop(seconds=2)
    async def restart_checker(self):
        if os.path.isfile("stop"):
            print("Stopping")
            await self.bot.close()
        elif os.path.isfile("restart"):
            os.remove("restart")
            print("Restarting")
            await self.bot.close()

    @commands.command()
    async def restart(self, ctx: SlashContext):
        open("restart", "w+").close()
        await send_embed(ctx, "", "Restarting")
        
    @commands.command()
    async def stop(self, ctx: SlashContext):
        open("stop", "w+").close()
        await send_embed(ctx, "", "Stopping")

def setup(bot):
    bot.add_cog(Main(bot))
