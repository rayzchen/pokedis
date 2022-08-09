from discord.ext import commands
from discord import ButtonStyle, slash_command, SelectOption
from utils import CustomView, CustomSelect, CustomButton, format_traceback, send_embed, create_embed, database, check_start, data, make_hp, EndCommand
import asyncio
import math

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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        error = format_traceback(err, False)
        await ctx.send("There was an error processing the command:\n" + error)

    @slash_command(name="start", description="Start your Pokémon journey!")
    async def start(self, ctx):
        try:
            if ctx.author.id in database.db["users"]:
                await send_embed(ctx, "Error", "You have already started PokéDis!", author=ctx.author)
                return
            view = CustomView(CustomButton(style=ButtonStyle.green, label="Talk"))
            msg = await send_embed(
                ctx, "Start", "Talk to Professor Oak.", author=ctx.author, view=view)
            await view.custom_wait(self.bot)

            for line in start_text:
                view = CustomView(CustomButton(style=ButtonStyle.green, label="Continue"))
                embed = create_embed("Professor Oak", "OAK - " + delim.join(line), author=ctx.author)
                await ctx.response.edit_message(embed=embed, view=view)
                await view.custom_wait(self.bot)

            embed = create_embed("Professor Oak", "OAK - **" + ctx.author.name.upper() + "**!", author=ctx.author)
            await ctx.response.edit_message(embed=embed)
            await view.custom_wait(self.bot)

            for line in start_text2:
                embed = create_embed("Professor Oak", "OAK - " + delim.join(line), author=ctx.author)
                await ctx.response.edit_message(embed=embed)
                await view.custom_wait(self.bot)
        except EndCommand:
            await ctx.reply("Player creation cancelled.")
            return
        except:
            raise

        starters = ["Bulbasaur", "Charmander", "Squirtle"]
        starterids = [1, 4, 7]

        buttons = [CustomButton(style=ButtonStyle.green, label=p) for p in starters]
        view = CustomView(*buttons)
        embed = create_embed("Starter Pokémon",
            "Which Pokémon would you like to select?\n\n1. __Bulbasaur__\nType: **Grass**\n\n2. __Charmnder__\nType: **Fire**\n\n3. __Squirtle__\nType: **Water**")
        await ctx.response.edit_message(embed=embed, view=view)
        await view.custom_wait(self.bot)

        pokemon = data.gen_pokemon(starterids[starters.index(view.current.label)], 5)
        user = {
            "inventory": [],
            "pc": [{"name": "Potion", "count": 1}],
            "rival": "Gary",
            "pokemon": [pokemon],
            "badges": [],
        }
        database.db["users"][ctx.author.id] = user

        view.disable_all_items()
        embed = create_embed("Starter Pokémon", f"You have chosen __{view.current.label}__ as your starter!")
        await ctx.response.edit_message(embed=embed, view=view)

    @slash_command(name="delete", description="Delete your account")
    @check_start
    async def delete(self, ctx):
        buttons = [CustomButton(style=ButtonStyle.green, label="No"),
                   CustomButton(style=ButtonStyle.green, label="Yes")]
        view = CustomView(*buttons)
        await send_embed(ctx, "Delete", "Are you sure you want to delete your account?\nThis process cannot be undone.", author=ctx.author, view=view)
        await view.custom_wait(self.bot)
        if view.current.label == "Yes":
            database.db["users"].pop(ctx.author.id)
            embed = create_embed("Delete", "Deleted account. You can restart with `/start`.")
        else:
            embed = create_embed("Delete", "Cancelled deleting account.")
        await ctx.response.edit(embed=embed, view=None)

    @slash_command(name="use", description="Use an item in your inventory")
    @check_start
    async def use(self, ctx, item):
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

    @slash_command(name="pc", description="Store and withdraw items from Bill's PC")
    @check_start
    async def pc(self, ctx):
        page = 1
        first = True
        buttons = [
            CustomButton(style=ButtonStyle.green, label="◀"),
            CustomButton(style=ButtonStyle.green, label="▶"),
            CustomButton(style=ButtonStyle.green, row=1, label="Deposit"),
            CustomButton(style=ButtonStyle.green, row=1, label="Withdraw"),
            CustomButton(style=ButtonStyle.green, row=1, label="Quit")
        ]
        while True:
            if len(database.db['users'][ctx.author.id]['pc']) == 0:
                page = 0
            elif page == 0 and len(database.db['users'][ctx.author.id]['pc']) != 0:
                page = 1
            viewing = database.db["users"][ctx.author.id]["pc"][(page - 1) * 10: page * 10]
            length = math.ceil(len(database.db['users'][ctx.author.id]['pc']) / 10)
            embed = create_embed("Bill's PC", "Here are your current items: \n\n" + "\n".join(["__" + item["name"] + "__ **(x" + str(item["count"]) + ")**" for item in viewing]), footer=f"Page {page} of {length}", author=ctx.author)
            buttons[0].disabled = page < 2
            buttons[1].disabled = page == length
            view = CustomView(*buttons)
            if first:
                await ctx.send_response(embed=embed, view=view)
                first = False
            else:
                await ctx.response.edit_message(embed=embed, view=view)
            await view.custom_wait(self.bot)
            if view.current.label == "Quit":
                view.disable_all_items()
                await ctx.response.edit_message(view=view)
                raise EndCommand
            if view.current.label == "◀":
                page -= 1
            elif view.current.label == "▶":
                page += 1
            elif view.current.label == "Deposit" or view.current.label == "Withdraw":
                if view.current.label == "Deposit":
                    verb = "deposit"
                    storage = "inventory"
                    other = "pc"
                    verb_past = "Deposited"
                    direction = "to"
                else:
                    verb = "withdraw"
                    storage = "pc"
                    other = "inventory"
                    verb_past = "Withdrew"
                    direction = "from"

                description = embed.description
                if len(database.db["users"][ctx.author.id][storage]) == 0:
                    embed.description += "\n\nYou have no items!"
                    button = CustomButton(style=ButtonStyle.green, label="OK")
                    view = CustomView(button)
                    await ctx.response.edit_message(embed=embed, view=view)
                    await view.custom_wait(self.bot)
                    embed.description = description
                    continue
                buttons = [
                    CustomButton(style=ButtonStyle.green, label="Cancel"),
                    CustomSelect(
                        row=1,
                        options=[SelectOption(label=item["name"], value=str(i)) for i, item in enumerate(database.db["users"][ctx.author.id][storage])],
                        placeholder="Choose item"
                    )
                ]
                embed.description += f"\n\nChoose an item to {verb}."
                view = CustomView(*buttons)
                await ctx.response.edit_message(embed=embed, view=view)
                await view.custom_wait(self.bot)
                if isinstance(view.current, CustomSelect):
                    item = int(view.current.values[0])
                    itemdata = database.db["users"][ctx.author.id][storage][item]
                    amount = 1
                    while True:
                        embed.description = description + f"\n\nHow many **{itemdata['name']}**s do you want to {verb}?\nNumber: {amount}"
                        buttons = [
                            CustomButton(style=ButtonStyle.green, label="-", disabled=amount == 1),
                            CustomButton(style=ButtonStyle.green, label="+", disabled=amount == itemdata["count"]),
                            CustomButton(style=ButtonStyle.green, label="Confirm")
                        ]
                        view = CustomView(*buttons)
                        await ctx.response.edit_message(embed=embed, components=[buttons])
                        await view.custom_wait(self.bot)
                        if view.current.label == "+":
                            amount += 1
                        elif view.current.label == "=":
                            amount -= 1
                        else:
                            break
                    button = CustomButton(style=ButtonStyle.green, label="OK")
                    view = CustomView(*button)
                    pc_item = None
                    for stored in database.db["users"][ctx.author.id][other]:
                        if stored["name"] == itemdata["name"]:
                            pc_item = stored
                    if pc_item is None:
                        database.db["users"][ctx.author.id][other].append({"name": itemdata["name"], "count": amount})
                    else:
                        stored["count"] += amount
                    itemdata["count"] -= amount
                    if itemdata["count"] == 0:
                        database.db["users"][ctx.author.id]["inventory"].pop(item)
                    embed.description = "Here are your current items: \n\n" + "\n".join(["__" + item["name"] + "__ **(x" + str(item["count"]) + ")**" for item in viewing]) + f"\n\n{verb_past} {amount} **{itemdata['name']}**" + ("s" if itemdata["count"] > 1 else "") + f" {direction} the PC."
                    await ctx.response.edit_message(embed=embed, view=view)
                    await view.custom_wait(self.bot)

    @slash_command(name="pokemon", description="View your Pokémon")
    @check_start
    async def pokemon(self, ctx):
        page = 0
        msg = None
        view = None
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

            buttons = [
                CustomButton(style=ButtonStyle.green, label="◀", disabled=page < 1),
                CustomButton(style=ButtonStyle.green, label="▶", disabled=page == len(database.db["users"][ctx.author.id]["pokemon"]) - 1)
            ]
            view = CustomView(*buttons)

            embed = create_embed("Pokémon", text, footer=f"{len(database.db['users'][ctx.author.id]['pokemon'])} Pokémon", author=ctx.author)
            embed.set_image(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/" + str(poke["species"]) + ".png")
            if msg is None:
                msg = await ctx.send_response(embed=embed, view=view)
            else:
                await ctx.response.edit_message(embed=embed, view=view)
            await view.custom_wait(self.bot)
            if view.current.label == "◀":
                page -= 1
            elif view.current.label == "▶":
                page += 1

    @slash_command(name="restore", description="Visit the Pokémon Center")
    @check_start
    async def restore(self, ctx):
        for poke in database.db["users"][ctx.author.id]["pokemon"]:
            poke["status"] = []
            poke["hp"] = poke["stats"]["hp"]
            data.calc_stats(poke)
            for i in range(4):
                if poke["moves"][i] == 0:
                    break
                poke["pp"][i] = data.all_move_data[str(poke["moves"][i])]["pp"]
        interaction = await send_embed(ctx, "Pokémon Center", "Healing Pokémon...", author=ctx.author)
        await asyncio.sleep(2)
        await interaction.edit_original_message(embed=create_embed("Pokémon Center", "Healed your Pokémon!\nWe hope to see you soon!", author=ctx.author))

def setup(bot):
    bot.add_cog(User(bot))
