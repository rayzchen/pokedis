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
        poke2 = data.gen_pokemon(165, 2)
        name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
        name2 = f"__Wild__ **{data.pokename(poke2['species'])}**"

        caption = "What would you like to do?"
        def get_text(caption):
            return f"{name1} **[Level {poke1['level']}]**\n**{poke1['hp']} / {poke1['stats']['hp']}**\n{make_hp(poke1['hp'] / poke1['stats']['hp'])}\n\n{name2} **[Level {poke2['level']}]**\n**{poke2['hp']} / {poke2['stats']['hp']}**\n{make_hp(poke2['hp'] / poke2['stats']['hp'])}\n\n{caption}"
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
                else:
                    caption += "\nSpecial effect!"
                    print(2)
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
                if outcome == 1:
                    win = outcome == winning
                    if win:
                        caption = f"{defname} fainted!"
                    else:
                        print(win)
                        caption = f"{atkname} fainted!"
                    await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                    await asyncio.sleep(2)
                    return 1, win
            return False

        embed = create_embed("Battle", get_text(caption))
        buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
        message = await ctx.send(embed=embed, components=[buttons])
        run_count = 0
        while True:
            button_ctx = await custom_wait(self.bot, message)

            action = button_ctx.component["label"]
            if action == "Fight":
                buttons = [create_actionrow(create_button(ButtonStyle.green, label=data.movename(move))) for move in poke1["moves"] if move != 0]
                moves = {data.movename(move): move for move in poke1["moves"] if move != 0}
                caption = "Choose a move."
                await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=buttons)
                button_ctx = await custom_wait(self.bot, message)
                selected = moves[button_ctx.component["label"]]

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
                caption = f"{atkname} uses __{button_ctx.component['label']}__!"
                
                outcome = await fight(atkname, defname, atkpoke, defpoke, selected, 1, caption)
                if outcome:
                    break
                
                caption = f"{defname} strikes back fiercely!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)))
                await asyncio.sleep(2)
                selected = defpoke["moves"][random.randint(0, 3 - defpoke["moves"].count(0))]
                caption = f"{defname} uses __{data.all_move_data[str(selected)]['name']}__!"

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
                    caption = f"{name2} uses __{data.all_move_data[str(selected)]['name']}__!"

                    outcome = await fight(name2, name1, poke2, poke1, selected, 2, caption)
                    if outcome:
                        break
            
            buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[buttons])
        
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
                    button_ctx = await custom_wait(self.bot, message)
                    forget = int(button_ctx.component["label"][0]) - 1
                    poke1["moves"][forget] = move
                    caption = f"{name1} forgot **{button_ctx.component['label'][4:]}** and learnt **{movedata['name']}**!"
                    await button_ctx.edit_origin(embed=create_embed("Battle", get_text(caption)), components=[])
                else:
                    poke1["moves"][poke1["moves"].index(0)] = move
                    caption = f"{name1} learnt **{movedata['name']}**!"
                await asyncio.sleep(2)
            
            caption = f"**{ctx.author.name}** earned **$500**!"
            await button_ctx.origin_message.edit(embed=create_embed("Battle", get_text(caption)), components=[])
            await asyncio.sleep(2)

def setup(bot):
    bot.add_cog(User(bot))
