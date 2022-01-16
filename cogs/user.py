from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button,create_select, create_select_option)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, database, check_start, data, make_hp, custom_wait, EndCommand
import asyncio
import math

main_server = 894254591858851871

start_text = [
    ["Hello there! Welcome to the", "world of Pokémon!"],
    ["My name is OAK! People call me", "the Pokémon PROF!"],
    ["This world is inhabited by", "creatures called Pokémon!"],
    ["For some people, Pokémon are", "pets. Others use them for fights."],
    ["Myself..."],
    ["I study Pokémon as a profession."],
]
delim = u"\n\u2800\u2800\u2800\u2800 "

start_text2 = [
    ["Your very own Pokémon journey", "is about to begin!"],
    ["A world of dreams and adventures", "with Pokémon awaits! Let's go!"],
]

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_slash(
        name="start", description="Start your Pokémon journey!",
        guild_ids=[main_server])
    async def start(self, ctx: SlashContext):
        try:
            if ctx.author.id in database.db["users"]:
                await send_embed(ctx, "Error", "You have already started PokéDis!", author=ctx.author)
                return
            buttons = create_actionrow(
                create_button(style=ButtonStyle.green, label="Talk"))
            msg = await send_embed(
                ctx, "Start", "Talk to Professor Oak.", author=ctx.author, components=[buttons])
            button_ctx = await custom_wait(self.bot, msg, buttons)

            for line in start_text:
                buttons = create_actionrow(
                    create_button(style=ButtonStyle.green, label="Continue"))
                embed = create_embed("Professor Oak", "OAK - " + delim.join(line), author=ctx.author)
                await button_ctx.edit_origin(embed=embed, components=[buttons])
                button_ctx = await custom_wait(self.bot, msg, buttons)
            
            buttons = create_actionrow(
                create_button(style=ButtonStyle.green, label="Continue"))
            embed = create_embed("Professor Oak", "OAK - **" + ctx.author.name.upper() + "**!", author=ctx.author)
            await button_ctx.edit_origin(embed=embed, components=[buttons])
            button_ctx = await custom_wait(self.bot, msg, buttons)

            for line in start_text2:
                buttons = create_actionrow(
                    create_button(style=ButtonStyle.green, label="Continue"))
                embed = create_embed("Professor Oak", "OAK - " + delim.join(line), author=ctx.author)
                await button_ctx.edit_origin(embed=embed, components=[buttons])
                button_ctx = await custom_wait(self.bot, msg, buttons)
        except EndCommand:
            await ctx.reply("Player creation cancelled.")
            return
        except:
            raise
        
        starters = ["Bulbasaur", "Charmander", "Squirtle"]

        buttons = create_actionrow(*[
            create_button(style=ButtonStyle.green, label=p) for p in starters])
        embed = create_embed("Starter Pokémon",
            "Which Pokémon would you like to select?\n\n1. __Bulbasaur__\nType: **Grass**\n\n2. __Charmnder__\nType: **Fire**\n\n3. __Squirtle__\nType: **Water**")
        await button_ctx.edit_origin(embed=embed, components=[buttons])
        button_ctx = await custom_wait(self.bot, msg, buttons)

        pokemon = data.gen_pokemon(starters.index(button_ctx.component["label"]) * 3 + 1, 5)
        user = {
            "inventory": [],
            "pc": [{"name": "Potion", "count": 1}],
            "rival": "Gary",
            "pokemon": [pokemon],
            "badges": [],
        }
        database.db["users"][ctx.author.id] = user

        buttons = create_actionrow(*[
            create_button(style=ButtonStyle.green, label=p) for p in starters])
        embed = create_embed("Starter Pokémon", f"You have chosen __{button_ctx.component['label']}__ as your starter!")
        button_ctx.edit_origin(embed=embed, components=[buttons])
    
    @cog_ext.cog_slash(
        name="use", description="Use an item in your inventory",
        guild_ids=[main_server])
    @check_start
    async def use(self, ctx: SlashContext, item):
        name = " ".join(map(str.capitalize, item.rstrip().lstrip().lower().split(" ")))
        if name not in data.items:
            await send_embed(ctx, "Error", f"Item __{name}__ does not exist!", author=ctx.author)
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
            await send_embed(ctx, "Error", f"You do not have a '__{name}__'!", author=ctx.author)
            return
        if remove != -1:
            inv.pop(remove)
        database.db["users"][ctx.author.id]["inventory"] = inv

        await send_embed(ctx, "Item", f"Used '__{name}__'", author=ctx.author)

    @cog_ext.cog_slash(
        name="pc", description="Store and withdraw items from Bill's PC", guild_ids=[main_server])
    @check_start
    async def pc(self, ctx: SlashContext):
        page = 1
        button_ctx = None
        row2 = create_actionrow(
            create_button(ButtonStyle.green, "Deposit"),
            create_button(ButtonStyle.green, "Withdraw"),
            create_button(ButtonStyle.green, "Quit"))
        while True:
            if len(database.db['users'][ctx.author.id]['pc']) == 0:
                page = 0
            elif page == 0 and len(database.db['users'][ctx.author.id]['pc']) != 0:
                page = 1
            viewing = database.db["users"][ctx.author.id]["pc"][(page - 1) * 10: page * 10]
            length = math.ceil(len(database.db['users'][ctx.author.id]['pc']) / 10)
            embed = create_embed("Bill's PC", "Here are your current items: \n\n" + "\n".join(["__" + item["name"] + "__ **(x" + str(item["count"]) + ")**" for item in viewing]), footer=f"Page {page} of {length}", author=ctx.author)
            buttons = create_actionrow(
                create_button(ButtonStyle.green, "◀", disabled=page < 2),
                create_button(ButtonStyle.green, "▶", disabled=page == length))
            if button_ctx is None:
                msg = await ctx.send(embed=embed, components=[buttons, row2])
            else:
                await button_ctx.edit_origin(embed=embed, components=[buttons, row2])
            button_ctx = await custom_wait(self.bot, msg, [buttons, row2])
            if button_ctx.component["label"] == "Quit":
                for component in buttons["components"]:
                    component["disabled"] = True
                for component in row2["components"]:
                    component["disabled"] = True
                await button_ctx.edit_origin(components=[buttons, row2])
                break
            if button_ctx.component["label"] == "◀":
                page -= 1
            elif button_ctx.component["label"] == "▶":
                page += 1
            elif button_ctx.component["label"] == "Deposit":
                description = embed.description
                if len(database.db["users"][ctx.author.id]["inventory"]) == 0:
                    embed.description += "\n\nYou have no items!"
                    buttons = create_actionrow(create_button(ButtonStyle.green, "OK"))
                    await button_ctx.edit_origin(embed=embed, components=[buttons])
                    button_ctx = await custom_wait(self.bot, msg, buttons)
                    embed.description = description
                    continue
                buttons = [
                    create_actionrow(create_button(ButtonStyle.green, "Cancel")),
                    create_actionrow(create_select(
                        options=[create_select_option(item["name"], str(i)) for i, item in enumerate(database.db["users"][ctx.author.id]["inventory"])],
                        placeholder="Choose item",
                        min_values=1
                    ))
                ]
                embed.description += "\n\nChoose an item to deposit."
                await button_ctx.edit_origin(embed=embed, components=buttons)
                button_ctx = await custom_wait(self.bot, msg, buttons)
                if button_ctx.selected_options is not None:
                    item = int(button_ctx.selected_options[0])
                    itemdata = database.db["users"][ctx.author.id]["inventory"][item]
                    amount = 1
                    while True:
                        embed.description = description + f"\n\nHow many **{itemdata['name']}**s do you want to deposit?\nNumber: {amount}"
                        buttons = create_actionrow(create_button(ButtonStyle.green, "-", disabled=amount == 1), create_button(ButtonStyle.green, "+", disabled=amount == itemdata["count"]), create_button(ButtonStyle.green, "Confirm"))
                        await button_ctx.edit_origin(embed=embed, components=[buttons])
                        button_ctx = await custom_wait(self.bot, msg, [buttons])
                        if button_ctx.component["label"] == "+":
                            amount += 1
                        elif button_ctx.component["label"] == "=":
                            amount -= 1
                        else:
                            break
                    buttons = create_actionrow(create_button(ButtonStyle.green, "OK"))
                    pc_item = None
                    for stored in database.db["users"][ctx.author.id]["pc"]:
                        if stored["name"] == itemdata["name"]:
                            pc_item = stored
                    if pc_item is None:
                        database.db["users"][ctx.author.id]["pc"].append({"name": itemdata["name"], "count": amount})
                    else:
                        stored["count"] += amount
                    itemdata["count"] -= amount
                    if itemdata["count"] == 0:
                        database.db["users"][ctx.author.id]["inventory"].pop(item)
                    embed.description = "Here are your current items: \n\n" + "\n".join(["__" + item["name"] + "__ **(x" + str(item["count"]) + ")**" for item in viewing]) + f"\n\nDeposited {amount} **{itemdata['name']}**" + ("s" if itemdata["count"] > 1 else "") + " to the PC."
                    await button_ctx.edit_origin(embed=embed, components=[buttons])
                    button_ctx = await custom_wait(self.bot, msg, [buttons])
            elif button_ctx.component["label"] == "Withdraw":
                description = embed.description
                if len(database.db["users"][ctx.author.id]["pc"]) == 0:
                    embed.description += "\n\nThe PC has no items!"
                    buttons = create_actionrow(create_button(ButtonStyle.green, "OK"))
                    await button_ctx.edit_origin(embed=embed, components=[buttons])
                    button_ctx = await custom_wait(self.bot, msg, buttons)
                    embed.description = description
                    continue
                buttons = [
                    create_actionrow(create_button(ButtonStyle.green, "Cancel")),
                    create_actionrow(create_select(
                        options=[create_select_option(item["name"], str(i)) for i, item in enumerate(database.db["users"][ctx.author.id]["pc"])],
                        placeholder="Choose item",
                        min_values=1
                    ))
                ]
                embed.description += "\n\nChoose an item to withdraw."
                await button_ctx.edit_origin(embed=embed, components=buttons)
                button_ctx = await custom_wait(self.bot, msg, buttons)
                if button_ctx.selected_options is not None:
                    item = int(button_ctx.selected_options[0])
                    itemdata = database.db["users"][ctx.author.id]["pc"][item]
                    amount = 1
                    while True:
                        embed.description = description + f"\n\nHow many **{itemdata['name']}**s do you want to withdraw?\nNumber: {amount}"
                        buttons = create_actionrow(create_button(ButtonStyle.green, "-", disabled=amount == 1), create_button(ButtonStyle.green, "+", disabled=amount == itemdata["count"]), create_button(ButtonStyle.green, "Confirm"))
                        await button_ctx.edit_origin(embed=embed, components=[buttons])
                        button_ctx = await custom_wait(self.bot, msg, [buttons])
                        if button_ctx.component["label"] == "+":
                            amount += 1
                        elif button_ctx.component["label"] == "=":
                            amount -= 1
                        else:
                            break
                    buttons = create_actionrow(create_button(ButtonStyle.green, "OK"))
                    inv_item = None
                    for stored in database.db["users"][ctx.author.id]["inventory"]:
                        if stored["name"] == itemdata["name"]:
                            inv_item = stored
                    if inv_item is None:
                        database.db["users"][ctx.author.id]["inventory"].append({"name": itemdata["name"], "count": amount})
                    else:
                        stored["count"] += amount
                    itemdata["count"] -= amount
                    if itemdata["count"] == 0:
                        database.db["users"][ctx.author.id]["pc"].pop(item)
                    embed.description = "Here are your current items: \n\n" + "\n".join(["__" + item["name"] + "__ **(x" + str(item["count"]) + ")**" for item in viewing]) + f"\n\nWithdrew {amount} **{itemdata['name']}**" + ("s" if itemdata["count"] > 1 else "") + " from the PC."
                    await button_ctx.edit_origin(embed=embed, components=[buttons])
                    button_ctx = await custom_wait(self.bot, msg, [buttons])

    @cog_ext.cog_slash(
        name="pokemon", description="View your Pokémon",
        guild_ids=[main_server])
    @check_start
    async def pokemon(self, ctx: SlashContext):
        page = 0
        msg = None
        button_ctx = None
        while True:
            text = ""
            poke = database.db["users"][ctx.author.id]["pokemon"][page]
            poke["level"] = data.get_level(poke["exp"], data.all_pokemon_data[str(poke["species"])]["growth"])
            lower = data.level_exp[data.all_pokemon_data[str(poke["species"])]["growth"]][poke["level"] - 1]
            upper = data.level_exp[data.all_pokemon_data[str(poke["species"])]["growth"]][poke["level"]]
            text += f"**{data.pokename(poke['species'])}** __Level {poke['level']}__\n**{poke['hp']} / {poke['stats']['hp']}**\n{make_hp(poke['hp'] / poke['stats']['hp'])}\nATK: {poke['stats']['atk']} DEF: {poke['stats']['def']}\nSPEC: {poke['stats']['spec']} SPD: {poke['stats']['spd']}\nEXP: {poke['exp'] - lower} / {upper - lower}\n\nMoves:\n"
            for i in range(4):
                if poke["moves"][i] == 0:
                    break
                text += f"**{data.movename(poke['moves'][i])}** - PP __{poke['pp'][i]} / {data.all_move_data[str(poke['moves'][i])]['pp']}__\n"

            buttons = create_actionrow(
                create_button(ButtonStyle.green, "◀", disabled=page < 1),
                create_button(ButtonStyle.green, "▶", disabled=page == len(database.db["users"][ctx.author.id]["pokemon"]) - 1))
            
            embed = create_embed("Pokémon", text, footer=f"{len(database.db['users'][ctx.author.id]['pokemon'])} Pokémon", author=ctx.author)
            embed.set_image(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/" + str(poke["species"]) + ".png")
            if msg is None:
                msg = await ctx.send(embed=embed, components=[buttons])
            else:
                await button_ctx.edit_origin(embed=embed, components=[buttons])
            button_ctx = await custom_wait(self.bot, msg, [buttons])
            if button_ctx.component["label"] == "◀":
                page -= 1
            elif button_ctx.component["label"] == "▶":
                page += 1
    
    @cog_ext.cog_slash(
        name="restore", description="Visit the Pokémon Center",
        guild_ids=[main_server])
    @check_start
    async def restore(self, ctx: SlashContext):
        for poke in database.db["users"][ctx.author.id]["pokemon"]:
            poke["status"] = []
            poke["hp"] = poke["stats"]["hp"]
            data.calc_stats(poke)
            for i in range(4):
                if poke["moves"][i] == 0:
                    break
                poke["pp"][i] = data.all_move_data[str(poke["moves"][i])]["pp"]
        msg = await send_embed(ctx, "Pokémon Center", "Healing Pokémon...", author=ctx.author)
        await asyncio.sleep(2)
        await msg.edit(embed=create_embed("Pokémon Center", "Healed your Pokémon!\nWe hope to see you soon!", author=ctx.author))

def setup(bot):
    bot.add_cog(User(bot))
