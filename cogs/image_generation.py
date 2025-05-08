import discord
from discord.ext import commands
import requests
import os
from config import *
from utils import react_with_random_emoji, log_error

class ImageGeneration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = STABILITY_API_URL
        self.api_key = STABILITY_API_KEY

    @commands.command(name='generate_image', help="Generates an image using the Stable Diffusion API")
    async def generate_image(self, ctx, *, prompt: str):
        await react_with_random_emoji(ctx.message)
        await ctx.send(f"Generating image for prompt: {prompt}...")
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "authorization": f"Bearer {self.api_key}",
                    "accept": "image/*"
                },
                files={"file": ("", "")},  # Dummy file for multipart/form-data
                data={
                    "prompt": prompt,
                    "output_format": "png"
                }
            )
            response.raise_for_status()
            
            # Save the generated image
            image_path = os.path.join(GENERATED_IMAGES_DIR, f"generated_{ctx.message.id}.png")
            with open(image_path, 'wb') as file:
                file.write(response.content)
            
            await ctx.send(file=discord.File(image_path))
            
        except requests.exceptions.HTTPError as http_err:
            error_details = response.json() if response.content else "No additional error details"
            await ctx.send(f"HTTP error occurred: {http_err}. Details: {error_details}")
            log_error(f"HTTP error in generate_image: {http_err}. Details: {error_details}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            log_error(f"Error in generate_image: {str(e)}")

async def setup(bot):
    await bot.add_cog(ImageGeneration(bot)) 