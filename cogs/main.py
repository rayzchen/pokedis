from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext
from utils import send_embed, create_embed, database
import os

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready")
        print("Logged in as:", self.bot.user)
        print("ID:", self.bot.user.id)
        self.restart_checker.start()
        for server in database.db["servers"].values():
            server["battling"] = []

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
    @commands.has_permissions(manage_guild=True)
    async def restart(self, ctx):
        open("restart", "w+").close()
        await send_embed(ctx, "", "Restarting")
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stop(self, ctx):
        open("stop", "w+").close()
        await send_embed(ctx, "", "Stopping")
    
    @cog_ext.cog_slash(
        name="reldb", description="Reload the database",
        guild_ids=[894254591858851871])
    async def reldb(self, ctx: SlashContext):
        message = await send_embed(ctx, "", "Reloading database...")
        database.db = database.Database("db.json")
        await message.edit(embed=create_embed("", "Reloaded database!"))

def setup(bot):
    bot.add_cog(Main(bot))
