from discord import slash_command, ButtonStyle # upm packge(pycord)
from discord.ext import commands, tasks # upm packge(pycord)
from discord.ui import Button, View # upm packge(pycord)
from utils import send_embed, create_embed, database, format_traceback, main_server, moderator_perms
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
        await ctx.send("There was an error processing the command:\n" + error)

    @tasks.loop(seconds=2)
    async def restart_checker(self):
        if os.path.isfile("stop"):
            print("Stopping")
            await self.bot.close()
        elif os.path.isfile("restart"):
            os.remove("restart")
            print("Restarting")
            await self.bot.close()

    @slash_command(name="restart", description="Restart the bot",
                   default_member_permissions=moderator_perms,
                   guild_ids=main_server)
    async def restart(self, ctx):
        open("restart", "w+").close()
        await send_embed(ctx, "", "Restarting")

    @slash_command(name="stop", description="Stop the bot",
                   default_member_permissions=moderator_perms,
                   guild_ids=main_server)
    async def stop(self, ctx):
        open("stop", "w+").close()
        await send_embed(ctx, "", "Stopping")

    @slash_command(name="reldb", description="Reload the database")
    async def reldb(self, ctx):
        message = await send_embed(ctx, "", "Reloading database...")
        database.db = database.Database("db.json")
        await message.edit(embed=create_embed("", "Reloaded database!"))

    @slash_command(name="invite", description="Invite this bot to your server")
    async def invite(self, ctx):
        invite = "https://discord.com/api/oauth2/authorize?client_id=894239120577159178&permissions=2147863616&scope=bot%20applications.commands"
        embed = create_embed("Invite", "Help expand the Pokédis community by inviting\nthis bot to your server!")
        button = Button(style=ButtonStyle.link, label="Invite me!", url=invite)
        await ctx.send(embed=embed, view=View(button))

def setup(bot):
    bot.add_cog(Main(bot))
