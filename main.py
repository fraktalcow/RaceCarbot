import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import asyncio
import requests
import google.generativeai as genai
import csv
import datetime
import logging
from config import *
from utils import setup_logging, ensure_directories, log_message, react_with_random_emoji, log_error

# Load environment variables
load_dotenv()
TOKEN = os.getenv('APIKEY')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Create bot instance with a custom help command
class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", description="Here's a list of available commands:", color=discord.Color.blue())
        for cog, cmds in mapping.items():
            command_signatures = [self.get_command_signature(cmd) for cmd in cmds]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Help for {command.name}", description=command.help, color=discord.Color.green())
        embed.add_field(name="Usage", value=self.get_command_signature(command))
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dictionary to store message response pairs
        self.command_responses = {}

bot = CustomBot(command_prefix=BOT_PREFIX, intents=intents, help_command=CustomHelpCommand())

# Utility function: React with a random emoji
async def react_with_random_emoji(message):
    emojis = ['⏳', '🔥', '✨', '🕑', '🤖', '💡', '🌟', '⚙️', '🌀', '🚀']
    emoji = random.choice(emojis)
    await message.add_reaction(emoji)

# Event: Bot is ready
@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="with commands"))
    logging.info(f'Bot started as {bot.user}')

# Event: Message received
@bot.event
async def on_message(message):
    if message.author != bot.user:
        print(f"{message.author.name}: {message.content}")
        log_message(message.id, message.author.name, message.content)
        
        # Store the channel's last message from the bot
        async for msg in message.channel.history(limit=1):
            if msg.author == bot.user:
                bot.command_responses[message.id] = msg.id
    
    await bot.process_commands(message)

# Event: Message edited
@bot.event
async def on_message_edit(before, after):
    if after.author != bot.user and before.content != after.content:
        # If the original message had a bot response, delete it
        if before.id in bot.command_responses:
            try:
                # Get the response message
                response_msg = await after.channel.fetch_message(bot.command_responses[before.id])
                # Delete the old response
                await response_msg.delete()
                # Remove the stored reference
                del bot.command_responses[before.id]
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass  # Message already deleted or can't be deleted
        
        # Process the edited message as a new command
        await bot.process_commands(after)

# Error handling with logging
@bot.event
async def on_command_error(ctx, error):
    await react_with_random_emoji(ctx.message)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I don't recognize that command. Type !help to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Oops! You're missing some required arguments. Type !help <command> for more info.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        log_error(error)

async def load_extensions():
    await bot.load_extension('cogs.image_generation')
    await bot.load_extension('cogs.retro_diffusion')
    await bot.load_extension('cogs.gemini_chat')
    await bot.load_extension('cogs.utility')
    await bot.load_extension('cogs.fun')
    # Add more cogs here as needed

async def main():
    # Setup
    setup_logging()
    ensure_directories()
    
    # Load extensions
    await load_extensions()
    
    # Start the bot
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
