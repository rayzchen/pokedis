from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import (
    create_actionrow, create_button, wait_for_component)
from discord_slash.model import ButtonStyle
from utils import create_embed, check_start, database, data
import asyncio

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_slash(
        name="battle", description="Test battle",
        guild_ids=[894254591858851871])
    @check_start
    async def battle(self, ctx: SlashContext):
        poke1 = database.db["users"][ctx.author.id]["pokemon"][0]
        poke2 = data.gen_pokemon(165, 2, ["normal", "normal"], [33, 39, 0, 0], [35, 30, 0, 0], [30, 56, 35, 25, 72])
        name1 = f"__{ctx.author.name}'s__ **{data.pokename(poke1['species'])}**"
        name2 = f"__Wild__ **{data.pokename(poke2['species'])}**"
        text = f"{name1} **[Level {poke1['level']}]**\n**%s / {poke1['stats']['hp']}**\n%s\n\n{name2} **[Level {poke2['level']}]**\n**%s / {poke2['stats']['hp']}**\n%s\n\n%s"
        fields = [
            poke1["hp"], "`HP BAR HP BAR HP BAR`", poke2["hp"],
            "`HP BAR HP BAR HP BAR`",
            "What would you like to do?"
        ]

        embed = create_embed("Battle", text % tuple(map(str, fields)))
        buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
        await ctx.send(embed=embed, components=[buttons])
        while True:
            button_ctx = await wait_for_component(self.bot, components=buttons)

            action = button_ctx.component["label"]
            if action == "Fight":
                fields[4] = f"{name1} has higher speed!\nIt attacks first!"
                await button_ctx.edit_origin(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
                await asyncio.sleep(2)
                fields[2] -= 10
                fields[4] = f"{name1} uses __Ember__!\nIt was very effective!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                fields[4] = f"{name2} strikes back fiercely!"
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                fields[0] -= 2
                fields[4] = f"{name2} used __Tackle__!\nIt wasn't very effective..."
                await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))))
                await asyncio.sleep(2)
                fields[4] = "What would you like to do?"
            elif action == "Run":
                fields[4] = "Ran away successfully!"
                await button_ctx.edit_origin(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[])
                return
            
            buttons = create_actionrow(create_button(ButtonStyle.green, "Fight"), create_button(ButtonStyle.green, "Item"), create_button(ButtonStyle.green, "Pokémon"), create_button(ButtonStyle.green, "Run"))
            await button_ctx.origin_message.edit(embed=create_embed("Battle", text % tuple(map(str, fields))), components=[buttons])

def setup(bot):
    bot.add_cog(User(bot))
