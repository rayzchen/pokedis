from . import db
import discord

def get_prefix(bot, ctx):
    return "p!"

async def send_embed(ctx, title, description, color=0x00CCFF):
    embed = discord.Embed(title=title, description=description, color=color)
    await ctx.send(embed=embed)
