# https://lucid.app/lucidchart/6a31915f-042e-4dec-be20-18997ad19643/edit?beaconFlowId=81B1E0515BD675DB&invitationId=inv_997cb4a9-99c5-469c-b13a-b3065593fccd&page=0_0#
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button)
from discord_slash.model import ButtonStyle
from utils import send_embed, create_embed, check_start, database, data, make_hp, custom_wait, EndCommand
import asyncio
import inspect
import random
import math
import time

effectiveness = {
    0: "It was not effective at all!",
    0.25: "It was not very effective...",
    0.5: "It was not very effective...",
    1: "",
    2: "It was super effective!",
    4: "It was extremely effective!",
}

def remove_channel_from_db(func):
    async def inner(self, ctx):
        try:
            await func(self, ctx)
        finally:
            if ctx.channel.id in database.db["servers"][ctx.guild.id]["battling"]:
                database.db["servers"][ctx.guild.id]["battling"].remove(ctx.channel.id)
    inner.__annotations__ = func.__annotations__
    inner.__signature__ = inspect.signature(func)
    return inner

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.id == self.bot.user.id and len(message.embeds) and message.embeds[0].title == "Battle":
            userid = int(message.embeds[0].author.icon_url.split("/")[4])
            user = await self.bot.fetch_user(userid)
            await send_embed(message.channel, "Forfeit", "You have forfeited the battle. Any HP, stats or level changes have been saved.", author=user)
            if message.guild.id in database.db["servers"] and message.channel.id in database.db["servers"][message.guild.id]["battling"]:
                database.db["servers"][message.guild.id]["battling"].remove(message.channel.id)
                print("Removed")
    
    @cog_ext.cog_slash(
        name="battle", description="Test battle",
        guild_ids=[894254591858851871])
    @remove_channel_from_db
    @check_start
    async def battle(self, ctx: SlashContext):
        # Check battling status
        if ctx.guild.id not in database.db["servers"]:
            database.db["servers"][ctx.guild.id] = {"battling": []}
        if ctx.channel.id in database.db["servers"][ctx.guild.id]["battling"]:
            await send_embed(ctx, "Error", "Someone is already battling in this channel!", author=ctx.author)
            return
        database.db["servers"][ctx.guild.id]["battling"].append(ctx.channel.id)

        # Select pokemon
        for poke in database.db["users"][ctx.author.id]["pokemon"]:
            if poke["hp"] > 0:
                poke1 = poke
                break
        else:
            raise EndCommand
        participated = [poke1]

        poke2 = data.gen_pokemon(random.choice([16, 16]), poke1["level"] + random.randint(-2, 2))
        name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
        name2 = f"__Wild__ **{data.pokename(poke2['species'])}**"

        # HP ATK DEF SP SPD ACC EV
        poke1["stat_change"] = [0, 0, 0, 0, 0, 0, 0]
        poke2["stat_change"] = [0, 0, 0, 0, 0, 0, 0]

        registers = [{}, {}]

        # Battle embed functions
        caption = ""
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
        
        # uuid = [poke1["species"], poke2["species"], uuid4()]
        # def get_image_link():
        #     if poke1["species"] != uuid[0]:
        #         uuid[0] = poke1["species"]
        #         uuid[2] = uuid4()
        #     elif poke2["species"] != uuid[1]:
        #         uuid[1] = poke2["species"]
        #         uuid[2] = uuid4()
        
        #     return f"https://pokedis-api.herokuapp.com/image?a={poke1['species']}&b={poke2['species']}&uuid={uuid[2]}"

        def get_image_link():
            return f"https://pokedis-api.herokuapp.com/image?a={poke1['species']}&b={poke2['species']}"
        
        async def send_battle_embed(buttons=None, cpt=None):
            if cpt is not None:
                embed = create_embed("Battle", get_text(cpt), author=ctx.author)
            else:
                embed = create_embed("Battle", get_text(caption), author=ctx.author)
            embed.set_image(url=get_image_link())
            await msg.edit(embed=embed, components=buttons)
        
        async def send_battle_embed2(buttons=[], cpt=None):
            await button_ctx.defer(edit_origin=True)
            await send_battle_embed(buttons, cpt)
        
        # Battle functions
        async def player_move(move):
            idx = poke1["moves"].index(move)
            poke1["pp"][idx] -= 1
            await fight(poke1, poke2, name1, name2, move)
        
        async def opp_move():
            move = poke2["moves"][random.randint(0, 3 - poke2["moves"].count(0))]
            await fight(poke2, poke1, name2, name1, move)
        
        async def fight(atkpoke, defpoke, atkname, defname, selected):
            caption = f"{atkname} used __{data.movename(selected)}__!"
            num = int(atkpoke is poke2)

            # Accuracy check
            # 0 accuracy means bypass accuracy checks
            if data.all_move_data[str(selected)]["acc"] != 0:
                modifiers = data.stat_modifiers2[atkpoke["stat_change"][5]] * data.stat_modifiers2[-defpoke["stat_change"][6]]
                print(modifiers)
                acc_threshold = random.randint(0, 100) * modifiers
                if acc_threshold > data.all_move_data[str(selected)]["acc"]:
                    await send_battle_embed([], cpt=caption)
                    await asyncio.sleep(2)
                    caption = f"{atkname} missed!"
                    await send_battle_embed(cpt=caption)
                    await asyncio.sleep(2)
                    return
            
            # Type of move
            if data.all_move_data[str(selected)]["effect"] != 1:
                # Physical damage
                dmg = data.get_damage(atkpoke, defpoke, selected)
                crit = data.is_crit(atkpoke, registers[num].get("crit", 1))
                if crit == 2:
                    caption += " **CRITICAL HIT!**"
                effective = data.get_effective(selected, defpoke)
                defpoke["hp"] -= int(dmg * crit * effective * (random.random() * 0.15 + 0.85))
                if effective != 1:
                    caption += "\n" + effectiveness[effective]
                if defpoke["hp"] <= 0:
                    defpoke["hp"] = 0
                await send_battle_embed([], cpt=caption)
                await asyncio.sleep(2)
                if defpoke["hp"] == 0:
                    return
                
                # Special move (not status)
                if str(selected) in data.special_move_data:
                    spec_move = data.special_move_data[str(selected)]
                    if "acc" in spec_move:
                        flag = random.randint(0, 100) <= spec_move["acc"]
                    else:
                        flag = True
                    if flag:
                        if "condition" in spec_move:
                            # Applies condition
                            if data.condition_resist[spec_move["condition"]] not in defpoke["types"] and spec_move["condition"] not in defpoke["status"]:
                                defpoke["status"].append(spec_move["condition"])
                                caption = f"{defname} is {data.conditions[spec_move['condition']]}"
                                await send_battle_embed(cpt=caption)
                                await asyncio.sleep(2)
                        elif "stat" in spec_move:
                            # Changes stat
                            defpoke["stat_change"][spec_move["stat"]] += spec_move["change"]
                            caption = f"{defname}'s **{data.stat_names[spec_move['stat']]}** stat was "
                            if spec_move["change"] > 0:
                                caption += "raised!"
                            else:
                                caption += "lowered!"
                            
                            change = defpoke["stat_change"][spec_move["stat"]]
                            original = list(defpoke["stats"].values())[spec_move["stat"]]
                            if change + original <= 0:
                                # Reset if effective stat is 0
                                defpoke["stat_change"][spec_move["stat"]] = -original
                            else:
                                await send_battle_embed(cpt=caption)
                                await asyncio.sleep(2)
            else:
                # Status move (or special damage calc)
                caption += "\nSpecial effect!"
                spec_move = data.special_move_data[str(selected)]

                # Targets
                # [adjacent foe][adjacent foe]
                # [self ally]   [adjacent ally]
                if spec_move["affects"][1] in ["foe", "any"]:
                    affected = (defpoke, defname)
                else:
                    affected = (atkpoke, atkname)
                
                end = False # for whirlwind
                if "stat" in spec_move:
                    # Stat modifier
                    affected[0]["stat_change"][spec_move["stat"]] += spec_move["change"]
                    new_caption = f"{affected[1]}'s **{data.stat_names[spec_move['stat']]}** stat was "
                    if spec_move["change"] > 0:
                        new_caption += "raised!"
                    else:
                        new_caption += "lowered!"
                    
                    change = affected[0]["stat_change"][spec_move["stat"]]
                    if abs(change) > 6:
                        # Clamp to -6 and 6
                        new_caption = "It had no effect!"
                        affected[0]["stat_change"][spec_move["stat"]] = min(max(change, -6), 6)
                elif "condition" in spec_move:
                    # Apply condition
                    if data.condition_resist[spec_move["condition"]] in defpoke["types"]:
                        # Resistant type
                        new_caption = "It had no effect!"
                    else:
                        affected[0]["status"].append(spec_move["condition"])
                        new_caption = f"{affected[1]} is {data.conditions[spec_move['condition']]}"
                        if spec_move["condition"] == 4:
                            # Badly poisoned turn counter
                            registers["bad_psn_turn"] = 0
                elif "critical" in spec_move:
                    registers[num]["crit"] = spec_move["critical"]
                    new_caption = f"{atkname}'s critical hit ratio rose!"
                
                ## Special moves (set effect to 1 and dont use anything above)
                elif selected == 18:
                    # Whirlwind
                    new_caption = f"{atkname} blew {defname} away!"
                    end = True
                elif selected == 73:
                    # Leech seed
                    if "seed" in registers[num]:
                        new_caption = "Nothing happened!"
                    else:
                        registers[num]["seed"] = 1
                        new_caption = f"A seed was planted in {defname}!"
                        if "grass" in defpoke["types"]:
                            new_caption += "\nIt doesn't affect it!"
                elif selected == 162:
                    # Super fang
                    poke2["hp"] -= min(1, poke2["hp"] // 2)
                    new_caption = ""
                
                await send_battle_embed([], cpt=caption)
                await asyncio.sleep(2)
                if new_caption:
                    await send_battle_embed(cpt=new_caption)
                    await asyncio.sleep(2)
                
                if end:
                    raise EndCommand
        
        def check_win():
            if poke2["hp"] <= 0:
                poke2["hp"] = 0
                return 1
            if poke1["hp"] <= 0:
                poke1["hp"] = 0
                return 2
            return 0
        
        async def apply_effect(poke, name):
            if 0 in poke["status"]:
                dmg = poke["stats"]["hp"] // 8
                poke["hp"] -= dmg
                if poke["hp"] < 0:
                    poke["hp"] = 0
                caption = f"{name} suffered __Burn__ damage!"
                await send_battle_embed(cpt=caption)
                await asyncio.sleep(2)
                if poke["hp"] == 0:
                    return True
            elif 3 in poke["status"]:
                dmg = poke["stats"]["hp"] // 8
                poke["hp"] -= dmg
                if poke["hp"] < 0:
                    poke["hp"] = 0
                caption = f"{name} suffered __Poison__ damage!"
                await send_battle_embed(cpt=caption)
                await asyncio.sleep(2)
                if poke["hp"] == 0:
                    return True
            return False
        
        async def apply_effects():
            ret = await apply_effect(poke1, name1)
            if ret:
                return
            await apply_effect(poke2, name2)

        caption = f"A wild **{data.pokename(poke2['species'])}** appeared!"
        embed = create_embed("Battle", get_text(caption), author=ctx.author)
        embed.set_image(url=get_image_link())
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(2)

        caption = f"Go, **{data.pokename(poke1['species'])}**!"
        await send_battle_embed()
        await asyncio.sleep(2)
        
        run_count = 0
        has_run_away = False
        outcome = 0 # 0 for no outcome, 1 for player, 2 for opponent

        ## MAIN LOOP
        while True:
            # Check for outcome (in case of switching out pokemon)
            if outcome == 1:
                break
            if outcome == 2:
                # Switch out
                caption = f"{name1} fainted!"
                if poke1 in participated:
                    participated.remove(poke1)
                await send_battle_embed()
                await asyncio.sleep(2)
                if all(poke["hp"] == 0 for poke in database.db["users"][ctx.author.id]["pokemon"]):
                    # Black out
                    caption = f"**{ctx.author.name}** has no usable pokémon!"
                    await send_battle_embed()
                    await asyncio.sleep(2)
                    caption = f"**{ctx.author.name}** blacked out!"
                    await send_battle_embed()

                    # Heal pokemon
                    for poke in database.db["users"][ctx.author.id]["pokemon"]:
                        poke["status"] = []
                        poke["hp"] = poke["stats"]["hp"]
                        data.calc_stats(poke)
                        for i in range(4):
                            if poke["moves"][i] == 0:
                                break
                            poke["pp"][i] = data.all_move_data[str(poke["moves"][i])]["pp"]
                    break
                caption = "Choose a Pokémon.\n\n"
                for i, poke in enumerate(database.db["users"][ctx.author.id]["pokemon"]):
                    caption += f":{data.numbers[i]}: __{data.pokename(poke['species'])}__ **[Level {poke['level']}]** {data.get_condition(poke)} **{poke['hp']} / {poke['stats']['hp']}**\n{make_hp(poke['hp'] / poke['stats']['hp'])}\n"
                buttons = [create_button(ButtonStyle.green, str(i + 1), disabled=len(database.db["users"][ctx.author.id]["pokemon"]) <= i or database.db["users"][ctx.author.id]["pokemon"][i]["hp"] == 0) for i in range(6)]
                buttons = [create_actionrow(*buttons[:3]), create_actionrow(*buttons[3:])]
                await send_battle_embed(buttons)

                button_ctx = await custom_wait(self.bot, msg, buttons)
                swap = database.db["users"][ctx.author.id]["pokemon"][int(button_ctx.component["label"]) - 1]
                
                # Reset pokemon stat changes and then swap
                del poke1["stat_change"]
                poke1 = swap
                poke1["stat_change"] = [0, 0, 0, 0, 0, 0, 0]
                name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
                if poke1 not in participated:
                    participated.append(poke1)

                caption = f"Go, **{data.pokename(poke1['species'])}**!"
                before = time.perf_counter() # wait 2 secs while image is uploading
                await send_battle_embed2([])

                remaining = before + 2.0 - time.perf_counter()
                await asyncio.sleep(remaining)

            # Send first prompt
            caption = "What would you like to do?"
            buttons = create_actionrow(
                create_button(ButtonStyle.green, "Fight"),
                create_button(ButtonStyle.green, "Item"),
                create_button(ButtonStyle.green, "Pokémon"),
                create_button(ButtonStyle.green, "Run"))
            await send_battle_embed([buttons])
            button_ctx = await custom_wait(self.bot, msg, [buttons])
            action = button_ctx.component["label"]

            player_second_fight = True # Player fights after if block?
            if action == "Fight":
                if poke1["pp"].count(0) == 4:
                    # No moves with PP left
                    caption = f"{name1} has no moves left!"
                    await send_battle_embed2()
                    await asyncio.sleep(2)
                    selected = 165 # Struggle
                else:
                    # Select move
                    buttons = [create_actionrow(create_button(ButtonStyle.green, label=data.movename(move) + f" - PP {poke1['pp'][i]}/{data.all_move_data[str(move)]['pp']}", disabled=poke1['pp'][i] == 0)) for i, move in enumerate(poke1["moves"]) if move != 0]
                    buttons.append(create_actionrow(create_button(ButtonStyle.green, label="Back")))
                    moves = {data.movename(move): move for move in poke1["moves"] if move != 0}
                    caption = "Choose a move."
                    await send_battle_embed2(buttons)

                    button_ctx = await custom_wait(self.bot, msg, buttons)
                    await button_ctx.defer(edit_origin=True)
                    if button_ctx.component["label"] == "Back":
                        continue
                    selected = moves[button_ctx.component["label"].split(" - ")[0]]

                priority = poke1["stats"]["spd"] >= poke2["stats"]["spd"]
                if priority:
                    await player_move(selected)
                    outcome = check_win()
                    if outcome > 0:
                        continue
                    player_second_fight = False
            elif action == "Pokémon":
                # Select pokemon
                caption = "Choose a Pokémon.\n\n"
                for i, poke in enumerate(database.db["users"][ctx.author.id]["pokemon"]):
                    caption += f":{data.numbers[i]}: __{data.pokename(poke['species'])}__ **[Level {poke['level']}]** {data.get_condition(poke)} **{poke['hp']} / {poke['stats']['hp']}**\n{make_hp(poke['hp'] / poke['stats']['hp'])}\n"
                buttons = [create_button(ButtonStyle.green, str(i + 1), disabled=len(database.db["users"][ctx.author.id]["pokemon"]) <= i or database.db["users"][ctx.author.id]["pokemon"][i]["hp"] == 0) for i in range(6)]
                buttons = [create_actionrow(*buttons[:3]), create_actionrow(*buttons[3:]), create_actionrow(create_button(ButtonStyle.green, "Back"))]
                await send_battle_embed2(buttons)

                button_ctx = await custom_wait(self.bot, msg, buttons)
                if button_ctx.component["label"] == "Back":
                    # Defer prompt so edit() works
                    await button_ctx.defer(edit_origin=True)
                    continue
                
                swap = database.db["users"][ctx.author.id]["pokemon"][int(button_ctx.component["label"]) - 1]
                if swap == poke1:
                    # Chose pokemon that's already on the field
                    caption = f"**{data.pokename(poke1['species'])}** is already out on the field!"
                    await send_battle_embed2([])
                    await asyncio.sleep(2)
                    continue
                
                caption = f"**{data.pokename(poke1['species'])}**, return!"
                before = time.perf_counter() # wait 2 secs while image is uploading
                await send_battle_embed2([])

                # Reset pokemon stat changes and then swap
                del poke1["stat_change"]
                poke1 = swap
                poke1["stat_change"] = [0, 0, 0, 0, 0, 0, 0]
                name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
                if poke1 not in participated:
                    participated.append(poke1)

                caption = f"Go, **{data.pokename(poke1['species'])}**!"
                remaining = before + 2.0 - time.perf_counter()
                await asyncio.sleep(remaining)
                await send_battle_embed()
                await asyncio.sleep(2)
                player_second_fight = False
            elif action == "Item":
                # Select item (NOT IMPLEMENTED YET)
                caption = "Not implemented yet!"
                await send_battle_embed2()
                await asyncio.sleep(2)
                player_second_fight = False
            elif action == "Run":
                # Check run status
                auto = math.floor(poke2["stats"]["spd"] / 4) % 256
                odds = math.floor(poke1["stats"]["spd"] * 32 / auto) + run_count * 30
                escape = auto == 0 or random.randint(0, 255) < odds
                
                if escape:
                    has_run_away = True
                    break
                caption = "Not fast enough!"
                await send_battle_embed2()
                await asyncio.sleep(2)
                player_second_fight = False
            
            # Opponent's turn
            await opp_move()
            outcome = check_win()
            if outcome > 0:
                continue

            if player_second_fight:
                await player_move(selected)
                outcome = check_win()
                if outcome > 0:
                    continue
            
            await apply_effects()
            outcome = check_win()
        
        # After main loop
        if has_run_away:
            caption = "Got away safely!"
            await send_battle_embed2()
        elif outcome == 1:
            # Player win
            caption = f"{name2} fainted!"
            await send_battle_embed()
            await asyncio.sleep(2)

            print(participated)

            # Earn XP
            gain = data.calc_exp_gain(ctx.author.id, poke1, poke2, True) // len(participated)
            for poke in participated:
                # Loop through each pokemon
                poke["exp"] += gain
                caption = f"__{ctx.author.name}'s__ **{data.pokename(poke['species'])}** earned **{gain} EXP**!"
                await send_battle_embed()
                await asyncio.sleep(2)

                # Increase EV
                lvl = data.get_level(poke["exp"], data.all_pokemon_data[str(poke["species"])]["growth"])
                for i in range(5):
                    poke["ev"][i] += data.all_pokemon_data[str(poke2["species"])]["base"][i]

                # Level up
                if lvl != poke["level"]:
                    caption = f"{name1} levelled up! {poke['level']} -> {lvl}\n"
                    poke["level"] = lvl
                    data.calc_stats(poke)
                    caption += f"ATK -> {poke['stats']['atk']} DEF -> {poke['stats']['def']}\nSPEC -> {poke['stats']['spec']} SPD -> {poke['stats']['spd']}"
                    await send_battle_embed()
                    await asyncio.sleep(4)

                    # Check new moves
                    if str(lvl) in data.all_pokemon_data[str(poke["species"])]["learnset"]:
                        move = data.all_pokemon_data[str(poke["species"])]["learnset"][str(lvl)]
                        movedata = data.all_move_data[str(move)]
                        if 0 not in poke["moves"]:
                            # Forget move
                            caption = f"{name1} is trying to learn **{movedata['name']}**, but it already knows 4 moves!\nWhich move would you like it to forget?"
                            components = [create_actionrow(create_button(ButtonStyle.green, f"{i} - " + data.all_move_data[str(move)]["name"])) for i, move in enumerate(poke["moves"])]
                            await send_battle_embed(components)
                            button_ctx = await custom_wait(self.bot, msg, components)
                            forget = int(button_ctx.component["label"][0]) - 1
                            poke["moves"][forget] = move
                            poke["pp"][forget] = data.all_move_data[str(move)]["pp"]
                            caption = f"{name1} forgot **{button_ctx.component['label'][4:]}** and learnt **{movedata['name']}**!"
                            await send_battle_embed2()
                        else:
                            # Add move
                            idx = poke["moves"].index(0)
                            poke["moves"][idx] = move
                            poke["pp"][idx] = data.all_move_data[str(move)]["pp"]
                            caption = f"{name1} learnt **{movedata['name']}**!"
                            await send_battle_embed()
                        await asyncio.sleep(2)
            
            # Add cash (temporarily)
            caption = f"**{ctx.author.name}** earned **$500**!"
            await send_battle_embed()
            await asyncio.sleep(2)

            await send_embed(
                ctx,
                "Victory <:pikahappy:906876093372448798>",
                f"Congratulations on defeating {name2}!\n" + \
                f"If you need to, heal up with `/restore`.")

def setup(bot):
    bot.add_cog(Battle(bot))
