from . import db
import discord

def get_prefix(bot, ctx):
    return "p!"

def create_embed(title, description, color=0x00CCFF):
    return discord.Embed(title=title, description=description, color=color)

async def send_embed(ctx, title, description, color=0x00CCFF, **kwargs):
    await ctx.send(embed=create_embed(title, description, color), **kwargs)
