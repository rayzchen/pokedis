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

        caption = "What would you like to do?"
        def get_text():
            return f"{name1} **[Level {poke1['level']}]**\n**{poke1['hp']} / {poke1['stats']['hp']}**\n{make_hp(poke1['hp'] / poke1['stats']['hp'])}\n\n{name2} **[Level {poke2['level']}]**\n**{poke2['hp']} / {poke2['stats']['hp']}**\n{make_hp(poke2['hp'] / poke2['stats']['hp'])}\n\n{caption}"

        embed = create_embed("Battle", get_text())
        buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
        await ctx.send(embed=embed, components=[buttons])
        while True:
            button_ctx = await wait_for_component(self.bot, components=buttons)

            action = button_ctx.component["label"]
            if action == "Fight":
                buttons = [create_actionrow(create_button(ButtonStyle.green, label=data.movename(move))) for move in poke1["moves"] if move != 0]
                moves = {data.movename(move): move for move in poke1["moves"] if move != 0}
                caption = "Choose a move."
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text()), components=buttons)
                button_ctx = await wait_for_component(self.bot, components=buttons)
                selected = moves[button_ctx.component["label"]]

                caption = f"{name1} has higher speed!\nIt attacks first!"
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text()), components=[])
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
                
                caption = f"{atkname} uses __{button_ctx.component['label']}__!"
                fields = [caption]
                outcome = self.fight(fields, atkname, defname, atkpoke, defpoke, selected)
                caption = fields[0]
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()))
                await asyncio.sleep(2)
                if outcome != 0:
                    win = outcome == 2
                    if win:
                        caption = f"{defname} fainted!"
                    else:
                        caption = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()))
                    await asyncio.sleep(2)
                    break
                
                caption = f"{defname} strikes back fiercely!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()))
                await asyncio.sleep(2)
                selected = defpoke["moves"][random.randint(0, 3 - poke2["moves"].count(0))]
                caption = f"{defname} uses __{data.all_move_data[str(selected)]['name']}__!"
                fields = [caption]
                outcome = self.fight(fields, defname, atkname, defpoke, atkpoke, selected, swp=2)
                caption = fields[0]
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()))
                await asyncio.sleep(2)
                if outcome != 0:
                    win = outcome == 1
                    if win:
                        caption = f"{defname} fainted!"
                    else:
                        caption = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()))
                    await asyncio.sleep(2)
                    break

                caption = "What would you like to do?"
            elif action == "Run":
                caption = "Ran away successfully!"
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text()), components=[])
                return
            
            buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()), components=[buttons])
        
        if win:
            gain = data.calc_exp_gain(ctx.author.id, poke1, poke2, True)
            poke1["exp"] += gain
            caption = f"{name1} earned **{gain} EXP**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()), components=[])
            await asyncio.sleep(2)

            lvl = data.get_level(poke1["exp"], data.all_pokemon_data[str(poke1["species"])]["growth"])
            if lvl != poke1["level"]:
                caption = f"{name1} levelled up! {poke1['level']} -> {lvl}\n"
                poke1["level"] = lvl
                data.calc_stats(poke1)
                for i in range(5):
                    poke1["ev"][i] += data.all_pokemon_data[str(poke2["species"])]["base"][i]
                caption += f"ATK -> {poke1['stats']['atk']} DEF -> {poke1['stats']['def']}\nSPEC -> {poke1['stats']['spec']} SPD -> {poke1['stats']['spd']}"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()), components=[])
                await asyncio.sleep(4)
            
            caption = f"**{ctx.author.name}** earned **$500**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text()), components=[])
            await asyncio.sleep(2)

    def fight(self, caption, name1, name2, poke1, poke2, selected, swp=0):
        if data.all_move_data[str(selected)]["effect"] != 1:
            dmg = data.get_damage(poke1, poke2, selected)
            print(dmg, data.get_damage(poke2, poke1, selected))
            crit = data.is_crit(poke1)
            if crit == 2:
                caption[0] += " **CRITICAL HIT!**"
            effective = data.get_effective(selected, poke2)
            poke2["hp"] -= int(dmg * crit * effective * (random.random() * 0.15 + 0.85))
            if effective != 1:
                caption[0] += "\n" + effectiveness[effective]
            if poke2["hp"] <= 0:
                poke2["hp"] = 0
                return 2
        else:
            caption[0] += "\nSpecial effect!"
        return 0

def setup(bot):
    bot.add_cog(User(bot))
