from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button, wait_for_component)
from discord_slash.model import ButtonStyle
from utils import create_embed, check_start, database, data, make_hp
import asyncio
import random

effectiveness = {
    0: "It was not effective at all!",
    0.25: "It was not very effective...",
    0.5: "It was not very effective...",
    1: "",
    2: "It was super effective!",
    4: "It was extremely effective!",
}

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_slash(
        name="battle", description="Test battle",
        guild_ids=[894254591858851871])
    @check_start
    async def battle(self, ctx: SlashContext):
        poke1 = database.db["users"][ctx.author.id]["pokemon"][0]
        poke2 = data.gen_pokemon(165, 2)
        name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
        name2 = f"__Wild__ **{data.pokename(poke2['species'])}**"
        text = f"{name1} **[Level {poke1['level']}]**\n**%s / {poke1['stats']['hp']}**\n%s\n\n{name2} **[Level {poke2['level']}]**\n**%s / {poke2['stats']['hp']}**\n%s\n\n%s"
        fields = [
            poke1["hp"], make_hp(poke1["hp"] / poke1["stats"]["hp"]), poke2["hp"],
            make_hp(poke2["hp"] / poke2["stats"]["hp"]),
            "What would you like to do?"
        ]

        embed = create_embed("Battle", text % tuple(map(str, fields)))
        buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
        await ctx.send(embed=embed, components=[buttons])
        while True:
            button_ctx = await wait_for_component(self.bot, components=buttons)

            action = button_ctx.component["label"]
            if action == "Fight":
                buttons = [create_actionrow(create_button(ButtonStyle.green, label=data.movename(move))) for move in poke1["moves"] if move != 0]
                moves = {data.movename(move): move for move in poke1["moves"] if move != 0}
                fields[4] = "Choose a move."
                await button_ctx.edit_origin(embed=create_embed("Battle", text % tuple(map(str, fields))), components=buttons)
                button_ctx = await wait_for_component(self.bot, components=buttons)
                selected = moves[button_ctx.component["label"]]

                fields[4] = f"{name1} has higher speed!\nIt attacks first!"
                await button_ctx.edit_origin(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
                await asyncio.sleep(2)
                
                if poke1["stats"]["spd"] > poke2["stats"]["spd"]:
                    atkname = name1
                    defname = name2
                    atkpoke = poke1
                    defpoke = poke2
                else:
                    atkname = name2
                    defname = name1
                    atkpoke = poke2
                    defpoke = poke1
                
                fields[4] = f"{atkname} uses __{button_ctx.component['label']}__!"
                outcome = self.fight(fields, atkname, defname, atkpoke, defpoke, selected)
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                if outcome != 0:
                    win = outcome == 2
                    if win:
                        fields[4] = f"{defname} fainted!"
                    else:
                        fields[4] = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                    await asyncio.sleep(2)
                    break
                
                fields[4] = f"{defname} strikes back fiercely!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                selected = defpoke["moves"][random.randint(0, 3 - poke2["moves"].count(0))]
                fields[4] = f"{defname} uses __{data.all_move_data[str(selected)]['name']}__!"
                outcome = self.fight(fields, defname, atkname, defpoke, atkpoke, selected, swp=2)
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                if outcome != 0:
                    win = outcome == 1
                    if win:
                        fields[4] = f"{defname} fainted!"
                    else:
                        fields[4] = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                    await asyncio.sleep(2)
                    break

                fields[4] = "What would you like to do?"
            elif action == "Run":
                fields[4] = "Ran away successfully!"
                await button_ctx.edit_origin(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
                return
            
            buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
            await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[buttons])
        
        if win:
            fields[4] = f"{name1} earned **200 EXP**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
            await asyncio.sleep(2)
            fields[4] = f"**{ctx.author.name}** earned **$500**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
            await asyncio.sleep(2)

    def fight(self, fields, name1, name2, poke1, poke2, selected, swp=0):
        if data.all_move_data[str(selected)]["effect"] != 1:
            dmg = data.get_damage(poke1, poke2, selected)
            print(dmg, data.get_damage(poke2, poke1, selected))
            crit = data.is_crit(poke1)
            if crit == 2:
                fields[4] += " **CRITICAL HIT!**"
            effective = data.get_effective(selected, poke2)
            fields[2 - swp] -= int(dmg * crit * effective * (random.random() * 0.15 + 0.85))
            poke2["hp"] = fields[2 - swp]
            fields[3 - swp] = make_hp(poke2["hp"] / poke2["stats"]["hp"])
            if effective != 1:
                fields[4] += "\n" + effectiveness[effective]
            if poke2["hp"] <= 0:
                poke2["hp"] = 0
                fields[2 - swp] = 0
                return 2
        else:
            fields[4] += "\nSpecial effect!"
        return 0

def setup(bot):
    bot.add_cog(User(bot))
