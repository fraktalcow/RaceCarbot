import discord
from discord.ext import commands
import random
from config import *
from utils import react_with_random_emoji, log_error

class Fun(commands.Cog):
    """Cog for fun and entertainment commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello', help='Responds with a friendly greeting')
    async def greet(self, ctx):
        """Send a friendly greeting to the user"""
        await react_with_random_emoji(ctx.message)
        await ctx.send(f'Hello {ctx.author.mention}! How can I assist you today?')
    
    @commands.command(name='flip', help='Flip a coin')
    async def flip_coin(self, ctx):
        """Flip a coin and get heads or tails"""
        await react_with_random_emoji(ctx.message)
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on: **{result}**", color=discord.Color.gold())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot)) 