import discord
from discord.ext import commands
import google.generativeai as genai
from config import *
from utils import react_with_random_emoji, log_error

class GeminiChat(commands.Cog):
    """Cog for interacting with Google's Gemini AI model"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_key = GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash-8b"
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.5,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
    @commands.command(name='ask', help='Ask Gemini AI a question')
    async def ask_gemini(self, ctx, *, question: str):
        """
        Ask Gemini AI a question and get a response
        Parameters:
            question (str): The question to ask Gemini AI
        """
        await react_with_random_emoji(ctx.message)
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                system_instruction="You are a very smart AI, u intellectually explain whatever i ask or give me all the info i need. use concise short intuitive summaries, use less words if needed.You URL links and sources blogs and such, based on the query",
            )
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(question)
            
            # Create and send response embed
            embed = discord.Embed(
                title="💭 Gemini AI Response",
                description=response.text,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Model: {self.model_name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            log_error(f"Error in ask_gemini: {str(e)}")

    @commands.command(name='gemini_info', help='Display information about the Gemini AI configuration')
    async def display_config(self, ctx):
        """Display the current configuration of the Gemini AI model"""
        embed = discord.Embed(
            title="Gemini AI Configuration",
            color=discord.Color.green()
        )
        embed.add_field(name="Model", value=self.model_name, inline=False)
        embed.add_field(name="Temperature", value=self.generation_config["temperature"], inline=True)
        embed.add_field(name="Top P", value=self.generation_config["top_p"], inline=True)
        embed.add_field(name="Top K", value=self.generation_config["top_k"], inline=True)
        embed.add_field(name="Max Tokens", value=self.generation_config["max_output_tokens"], inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GeminiChat(bot)) 