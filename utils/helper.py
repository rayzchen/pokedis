from . import database
import discord
import inspect

def get_prefix(bot, ctx):
    return "p!"

def create_embed(title, description, color=0x00CCFF):
    return discord.Embed(title=title, description=description, color=color)

async def send_embed(ctx, title, description, color=0x00CCFF, **kwargs):
    await ctx.send(embed=create_embed(title, description, color), **kwargs)

def check_start(func):
    async def inner(self, ctx, *args, **kwargs):
        if ctx.author.id not in database.db["users"]:
            await send_embed(ctx, "Error", "You have not started your Pokémon journey!")
            return
        await func(self, ctx, *args, **kwargs)
    inner.__annotations__ = func.__annotations__
    inner.__signature__ = inspect.signature(func)
    return inner

emojis = [
    "<:full1g:894733223979012157>",
    "<:full2g:894733224083882034>",
    "<:full3g:894733224012566569>",
    "<:half1g:894733223983206450>",
    "<:half2g:894733223672832091>",
    "<:half3g:894733224004173865>",

    "<:full1y:894733224016740382>",
    "<:full2y:894733223953846383>",
    "<:full3y:894733224016740372>",
    "<:half1y:894733223995768872>",
    "<:half2y:894733223907692555>",
    "<:half3y:894733223664439377>",

    "<:full1r:894733224020959232>",
    "<:full2r:894733223647670283>",
    "<:full3r:894733224008384512>",
    "<:half1r:894733223970603039>",
    "<:half2r:894733223643455589>",
    "<:half3r:894733223987396659>",

    "<:empty1:894737264238817281>",
    "<:empty2:894737264062656572>",
    "<:empty3:894737334594056202>"
]
def make_hp(amount):
    if amount == 0:
        return emojis[-3] + emojis[-2] * 8 + emojis[-1]
    if amount > 0.5:
        color = 0
    elif amount > 0.1:
        color = 1
    else:
        color = 2
    
    bar = [0 for _ in range(10)]
    end = int(amount * 10)
    for i in range(end):
        bar[i] = 2
    if amount * 10 - end >= 0.5:
        bar[end] = 1
    
    if bar[0] == 0:
        text = emojis[-3]
    elif bar[0] == 1:
        text = emojis[color * 6 + 3]
    else:
        text = emojis[color * 6]
    for item in bar[1:-1]:
        if item == 0:
            text += emojis[-2]
        elif item == 1:
            text += emojis[color * 6 + 4]
        else:
            text += emojis[color * 6 + 1]
    if bar[-1] == 0:
        text += emojis[-1]
    elif bar[-1] == 1:
        text += emojis[color * 6 + 5]
    else:
        text += emojis[color * 6 + 2]
    return text