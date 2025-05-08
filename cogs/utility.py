import discord
from discord.ext import commands
import platform
import psutil
import datetime
from config import *
from utils import react_with_random_emoji, log_error

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo', help='Displays information about the server')
    async def server_info(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"{guild.name} Server Information", color=discord.Color.blue())
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='userinfo', help='Displays information about a user')
    async def user_info(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        
        embed = discord.Embed(title=f"{member.name}'s Information", color=discord.Color.green())
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick if member.nick else "None", inline=True)
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='info', help='Displays information about the bot')
    async def display_info(self, ctx):
        embed = discord.Embed(title=f"{self.bot.user.name} Information", color=discord.Color.gold())
        
        # Bot stats
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        
        # System stats
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        
        # Resource usage
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{psutil.virtual_memory().percent}%", inline=True)
        
        # Uptime (if you track when the bot started)
        if hasattr(self.bot, 'start_time'):
            uptime = datetime.datetime.now() - self.bot.start_time
            embed.add_field(name="Uptime", value=f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m", inline=True)
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            
        await ctx.send(embed=embed)

    @commands.command(name='ping', help="Checks the bot's latency")
    async def check_ping(self, ctx):
        await react_with_random_emoji(ctx.message)
        start_time = datetime.datetime.now()
        message = await ctx.send("Pinging...")
        end_time = datetime.datetime.now()
        
        api_latency = round(self.bot.latency * 1000)
        response_time = (end_time - start_time).total_seconds() * 1000
        
        embed = discord.Embed(title="Pong! 🏓", color=discord.Color.green())
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Response Time", value=f"{round(response_time)}ms", inline=True)
        
        await message.edit(content=None, embed=embed)

    @commands.command(name='roles', help='Lists all roles in the server')
    async def list_roles(self, ctx):
        roles = sorted(ctx.guild.roles, key=lambda x: x.position, reverse=True)
        role_list = [f"{role.mention} - {len(role.members)} members" for role in roles if role.name != "@everyone"]
        
        embed = discord.Embed(title=f"Roles in {ctx.guild.name}", color=discord.Color.blue())
        
        # Split into chunks if too many roles
        chunks = [role_list[i:i + 10] for i in range(0, len(role_list), 10)]
        
        for i, chunk in enumerate(chunks):
            embed.add_field(name=f"Roles {i*10+1}-{i*10+len(chunk)}", value="\n".join(chunk), inline=False)
            
        await ctx.send(embed=embed)

async def setup(bot):
    try:
        import psutil
        await bot.add_cog(Utility(bot))
    except ImportError:
        print("psutil is not installed. Installing for system monitoring...")
        await bot.add_cog(Utility(bot)) 