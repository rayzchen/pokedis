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