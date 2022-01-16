from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, database, format_traceback, main_server
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        error = format_traceback(err, False)
        await ctx.send("There was an error processing the command:" + "\n" + error)

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
        if ctx.guild.id != main_server[0]:
            return
        open("restart", "w+").close()
        await send_embed(ctx, "", "Restarting")
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def stop(self, ctx):
        if ctx.guild.id != main_server[0]:
            return
        open("stop", "w+").close()
        await send_embed(ctx, "", "Stopping")
    
    @cog_ext.cog_slash(
        name="reldb", description="Reload the database",
        guild_ids=main_server)
    async def reldb(self, ctx: SlashContext):
        message = await send_embed(ctx, "", "Reloading database...")
        database.db = database.Database("db.json")
        await message.edit(embed=create_embed("", "Reloaded database!"))
    
    @cog_ext.cog_slash(
        name="invite", description="Invite this bot to your server",
        guild_ids=main_server)
    async def invite(self, ctx: SlashContext):
        invite = "https://discord.com/api/oauth2/authorize?client_id=894239120577159178&permissions=2147863616&scope=bot%20applications.commands"
        embed = create_embed("Invite", "Help expand the Pokédis community by inviting\nthis bot to your server!")
        buttons = create_actionrow(create_button(ButtonStyle.URL, "Invite me!", url=invite))
        await ctx.send(embed=embed, components=[buttons])

def setup(bot):
    bot.add_cog(Main(bot))
