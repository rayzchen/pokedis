from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button, wait_for_component)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, database, check_start, data
import copy

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
            await send_embed(ctx, "Error", "You have already started PokéDis!")
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
        
        charmander = data.gen_pokemon(176, 5, ["fire", "fire"], [10, 45, 0, 0], [35, 40, 0, 0], [39, 52, 32, 50, 65])
        user = {
            "inventory": [],
            "pc": [{"name": "potion", "count": 1}],
            "rival": "Gary",
            "pokemon": [charmander],
            "badges": [],
        }
        database.db["users"][ctx.author.id] = user
    
    @cog_ext.cog_slash(
        name="use", description="Use an item in your inventory",
        guild_ids=[894254591858851871])
    @check_start
    async def use(self, ctx: SlashContext, item):
        name = item.rstrip().lstrip().lower()
        if name not in data.items:
            await send_embed(ctx, "Error", f"Item {name} does not exist!")
            return

        inv = database.db["users"][ctx.author.id]["inventory"]
        remove = -1
        for i, item in enumerate(inv):
            if item["name"] == name:
                item["count"] -= 1
                if item["count"] == 0:
                    remove = i
                break
        else:
            await send_embed(ctx, "Error", f"You do not have a '__{item}__'!")
            return
        if remove != -1:
            inv.pop(remove)
        database.db["users"][ctx.author.id]["inventory"] = inv

        await send_embed(ctx, "Item", f"Used '__{item}__'")

def setup(bot):
    bot.add_cog(User(bot))
