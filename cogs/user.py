from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button, wait_for_component)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, database

start_text = [
    ["Hello there! Welcome to the", "world of POKéMON!"],
    ["My name is OAK! People call me", "the POKéMON PROF!"],
    ["This world is inhabited by", "creatures called POKéMON!"],
    ["For some people, POKéMON are", "pets. Others use them for fights."],
    ["Myself..."],
    ["I study POKéMON as a profession."],
]
delim = u"\n\u2800\u2800\u2800\u2800 "

start_text2 = [
    ["Your very own POKéMON journey", "is about to begin!"],
    ["A world of dreams and adventures", "with POKéMON awaits! Let's go!"],
]

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_slash(
        name="start", description="Start your Pokémon journey!",
        guild_ids=[894254591858851871])
    async def start(self, ctx: SlashContext):
        if ctx.author.id in database.db["users"]:
            await send_embed("Error", "You have already started PokéDis!")
            return
        buttons = create_actionrow(
            create_button(style=ButtonStyle.green, label="Talk"))
        await send_embed(
            ctx, "Start", "Talk to Professor Oak.", components=[buttons])
        button_ctx = await wait_for_component(self.bot, components=buttons)

        for line in start_text:
            buttons = create_actionrow(
                create_button(style=ButtonStyle.green, label="Continue"))
            embed = create_embed("Professor Oak", "OAK - " + delim.join(line))
            await button_ctx.edit_origin(embed=embed, components=[buttons])
            button_ctx = await wait_for_component(self.bot, components=buttons)
        
        buttons = create_actionrow(
            create_button(style=ButtonStyle.green, label="Continue"))
        embed = create_embed("Professor Oak", "OAK - **" + ctx.author.name.upper() + "**!")
        await button_ctx.edit_origin(embed=embed, components=[buttons])
        button_ctx = await wait_for_component(self.bot, components=buttons)

        for line in start_text2:
            buttons = create_actionrow(
                create_button(style=ButtonStyle.green, label="Continue"))
            embed = create_embed("Professor Oak", "OAK - " + delim.join(line))
            await button_ctx.edit_origin(embed=embed, components=[buttons])
            button_ctx = await wait_for_component(self.bot, components=buttons)
        
        embed = create_embed("Start", "Use /help for help with commands.")
        await button_ctx.edit_origin(embed=embed, components=[])
        
        user = {
            "inventory": [],
            "pc": [{"name": "potion", "count": 1}],
            "rival": "Gary",
            "pokemon": [],
            "badges": [],
        }
        database.db["users"][ctx.author.id] = user

def setup(bot):
    bot.add_cog(User(bot))
