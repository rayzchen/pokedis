from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, check_start, database, data, make_hp, custom_wait
import asyncio
import random
import math

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
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.id == self.bot.user.id and len(message.embeds) and message.embeds[0].title == "Battle":
            await send_embed(message.channel, "Forfeit", "You have forfeited the battle. Any HP, stats or level changes have been saved.")
    
    @cog_ext.cog_slash(
        name="battle", description="Test battle",
        guild_ids=[894254591858851871])
    @check_start
    async def battle(self, ctx: SlashContext):
        poke1 = database.db["users"][ctx.author.id]["pokemon"][0]
        poke2 = data.gen_pokemon(19, 2)
        name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
        name2 = f"__Wild__ **{data.pokename(poke2['species'])}**"

        poke1["stat_change"] = [0, 0, 0, 0, 0]
        poke2["stat_change"] = [0, 0, 0, 0, 0]

        registers = {}

        def get_text(caption):
            return "\n".join([
                f"{name1} **[Level {poke1['level']}]**{data.get_condition(poke1)}",
                f"**{poke1['hp']} / {poke1['stats']['hp']}**",
                f"{make_hp(poke1['hp'] / poke1['stats']['hp'])}",
                f"",
                f"{name2} **[Level {poke2['level']}]**{data.get_condition(poke2)}",
                f"**{poke2['hp']} / {poke2['stats']['hp']}**",
                f"{make_hp(poke2['hp'] / poke2['stats']['hp'])}",
                f"",
                f"{caption}"
            ])
        
        async def fight(atkname, defname, atkpoke, defpoke, selected, winning, caption):
            if random.randint(0, 99) > data.all_move_data[str(selected)]["acc"]:
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
                caption = f"{atkname} missed!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
            else:
                outcome = 0
                if data.all_move_data[str(selected)]["effect"] != 1:
                    dmg = data.get_damage(atkpoke, defpoke, selected)
                    crit = data.is_crit(atkpoke)
                    if crit == 2:
                        caption += " **CRITICAL HIT!**"
                    effective = data.get_effective(selected, defpoke)
                    defpoke["hp"] -= int(dmg * crit * effective * (random.random() * 0.15 + 0.85))
                    if effective != 1:
                        caption += "\n" + effectiveness[effective]
                    if defpoke["hp"] <= 0:
                        defpoke["hp"] = 0
                        outcome = 1
                    
                    if str(selected) in data.special_move_data:
                        spec_move = data.special_move_data[str(selected)]
                        if data.condition_resist[spec_move["condition"]] not in defpoke["types"]:
                            if random.randint(0, 100) <= spec_move["acc"]:
                                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                                await asyncio.sleep(2)
                                defpoke["status"].append(spec_move["condition"])
                                caption = f"{defname} is {data.conditions[spec_move['condition']]}"
                else:
                    caption += "\nSpecial effect!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)
                    spec_move = data.special_move_data[str(selected)]
                    if "foe" in spec_move["affects"]:
                        affected = (defpoke, defname)
                    else:
                        affected = (atkpoke, atkname)
                    if "stat" in spec_move:
                        affected[0]["stat_change"][spec_move["stat"]] += spec_move["change"]
                        caption = f"{affected[1]}'s **{data.stat_names[spec_move['stat']]}** stat was "
                        if spec_move["change"] > 0:
                            caption += "raised!"
                        else:
                            caption += "lowered!"
                        if affected[0]["stat_change"][spec_move["stat"]] > list(affected[0]["stats"].values())[spec_move["stat"]]:
                            caption = "It had no effect!"
                            affected[0]["stat_change"][spec_move["stat"]] = list(affected[0]["stats"].values())[spec_move["stat"]]
                        print(affected[0]["stat_change"])
                    elif data.condition_resist[spec_move["condition"]] in defpoke["types"]:
                        caption = "It had no effect!"
                    else:
                        affected[0]["status"].append(spec_move["condition"])
                        caption = f"{affected[1]} is {data.conditions[spec_move['condition']]}"
                
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
                if outcome == 1:
                    win = outcome == winning
                    if win:
                        caption = f"{defname} fainted!"
                    else:
                        caption = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)
                    return 1, win
            return False

        caption = f"A wild **{data.pokename(poke2['species'])}** appeared!"
        msg = await ctx.send(embed=create_embed("Battle", get_text(caption)))
        await asyncio.sleep(2)
        caption = f"Go, **{data.pokename(poke1['species'])}**!"
        await msg.edit(embed=create_embed("Battle", get_text(caption)))
        await asyncio.sleep(2)
        caption = "What would you like to do?"

        embed = create_embed("Battle", get_text(caption))
        buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
        message = await msg.edit(embed=embed, components=[buttons])
        run_count = 0
        while True:
            button_ctx = await custom_wait(self.bot, message, [buttons])

            action = button_ctx.component["label"]
            if action == "Fight":
                if poke1["pp"].count(0) == 4:
                    caption = f"{name1} has no moves left!"
                    await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
                    await asyncio.sleep(2)
                    caption = f"{name1} used __Struggle__!"
                    dmg = data.get_damage(poke1, poke2, 165) * (random.random() * 0.15 + 0.85)
                    poke2["hp"] -= round(dmg)

                    if poke2["hp"] <= 0:
                        poke2["hp"] = 0
                        outcome = (1, True)
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                        await asyncio.sleep(2)
                        caption = f"{name2} fainted!"
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                        await asyncio.sleep(2)
                        break

                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)
                    caption = f"{name1} is affected by recoil!"
                    poke1["hp"] -= round(dmg / 4)
                    
                    if poke1["hp"] <= 0:
                        poke1["hp"] = 0
                        outcome = (1, False)
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                        await asyncio.sleep(2)
                        caption = f"{name1} fainted!"
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                        await asyncio.sleep(2)
                        break

                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)
                    continue
                buttons = [create_actionrow(create_button(ButtonStyle.green, label=data.movename(move) + f" - PP {poke1['pp'][i]}/{data.all_move_data[str(move)]['pp']}", disabled=poke1['pp'][i] == 0)) for i, move in enumerate(poke1["moves"]) if move != 0]
                moves = {data.movename(move): move for move in poke1["moves"] if move != 0}
                caption = "Choose a move."
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=buttons)
                button_ctx = await custom_wait(self.bot, message, buttons)
                selected = moves[button_ctx.component["label"].split(" - ")[0]]

                caption = f"{name1} has higher speed!\nIt attacks first!"
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
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
                caption = f"{atkname} used __{button_ctx.component['label'].split(' - ')[0]}__!"
                poke1["pp"][poke1["moves"].index(selected)] -= 1
                
                outcome = await fight(atkname, defname, atkpoke, defpoke, selected, 1, caption)
                if outcome:
                    break
                
                caption = f"{defname} strikes back fiercely!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
                selected = defpoke["moves"][random.randint(0, 3 - defpoke["moves"].count(0))]
                caption = f"{defname} used __{data.all_move_data[str(selected)]['name']}__!"

                outcome = await fight(defname, atkname, defpoke, atkpoke, selected, 2, caption)
                if outcome:
                    break

                caption = "What would you like to do?"
            elif action == "Run":
                auto = math.floor(poke2["stats"]["spd"] / 4) % 256
                if auto == 0:
                    escape = True
                else:
                    odds = math.floor(poke1["stats"]["spd"] * 32 / auto) + run_count * 30
                    if odds > 255:
                        escape = True
                    else:
                        escape = random.randint(0, 255) < odds
                if escape:
                    caption = "Got away safely!"
                    await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
                    return
                else:
                    caption = "Not fast enough!"
                    await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
                    await asyncio.sleep(2)
                    run_count += 1
                    
                    caption = f"{name2} strikes!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)

                    selected = poke2["moves"][random.randint(0, 3 - poke2["moves"].count(0))]
                    caption = f"{name2} used __{data.all_move_data[str(selected)]['name']}__!"

                    outcome = await fight(name2, name1, poke2, poke1, selected, 2, caption)
                    if outcome:
                        break
            
            buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[buttons])
        
        del poke1["stat_change"]
        if outcome[1]:
            gain = data.calc_exp_gain(ctx.author.id, poke1, poke2, True)
            poke1["exp"] += gain
            caption = f"{name1} earned **{gain} EXP**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[])
            await asyncio.sleep(2)

            lvl = data.get_level(poke1["exp"], data.all_pokemon_data[str(poke1["species"])]["growth"])
            for i in range(5):
                poke1["ev"][i] += data.all_pokemon_data[str(poke2["species"])]["base"][i]
            if lvl != poke1["level"]:
                caption = f"{name1} levelled up! {poke1['level']} -> {lvl}\n"
                poke1["level"] = lvl
                data.calc_stats(poke1)
                caption += f"ATK -> {poke1['stats']['atk']} DEF -> {poke1['stats']['def']}\nSPEC -> {poke1['stats']['spec']} SPD -> {poke1['stats']['spd']}"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[])
                await asyncio.sleep(4)
                if str(lvl) in data.all_pokemon_data[str(poke1["species"])]["learnset"]:
                    move = data.all_pokemon_data[str(poke1["species"])]["learnset"][str(lvl)]
                    movedata = data.all_move_data[str(move)]
                    if 0 not in poke1["moves"]:
                        caption = f"{name1} is trying to learn **{movedata['name']}**, but it already knows 4 moves!\nWhich move would you like it to forget?"
                        components = [create_actionrow(create_button(ButtonStyle.green, f"{i} - " + data.all_move_data[str(move)]["name"])) for i, move in enumerate(poke1["moves"])]
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=components)
                        button_ctx = await custom_wait(self.bot, message, components)
                        forget = int(button_ctx.component["label"][0]) - 1
                        poke1["moves"][forget] = move
                        caption = f"{name1} forgot **{button_ctx.component['label'][4:]}** and learnt **{movedata['name']}**!"
                        await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
                    else:
                        poke1["moves"][poke1["moves"].index(0)] = move
                        caption = f"{name1} learnt **{movedata['name']}**!"
                        await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[])
                    await asyncio.sleep(2)
            
            caption = f"**{ctx.author.name}** earned **$500**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[])
            await asyncio.sleep(2)

def setup(bot):
    bot.add_cog(User(bot))
