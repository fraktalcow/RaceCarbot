import discord
from discord.ext import commands
import requests
import os
import base64
import io
from config import *
from utils import react_with_random_emoji, log_error

class RetroDiffusion(commands.Cog):
    """Cog for generating retro-style images using RetroAI Diffusion"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_url = RETRO_API_URL
        self.api_key = RETRO_API_KEY  # Use the config variable instead of direct env access
        if not self.api_key:
            log_error("RetroAI API key not found in environment variables")
            print("RetroAI API key not found. Please check your .env file.")

    @commands.command(name='retro', help="Generates a retro-style image from text prompt")
    async def generate_retro(self, ctx, *, prompt: str):
        """
        Generate a retro-style image using RetroAI
        Parameters:
            prompt (str): The text prompt for image generation
        """
        if not self.api_key:
            await ctx.send("⚠️ RetroAI API key not configured. Please set the RETRO_API_KEY environment variable.")
            return

        await react_with_random_emoji(ctx.message)
        status_message = await ctx.send(f"🎨 Generating retro-style image for prompt: {prompt}...")
        
        try:
            headers = {
                "X-RD-Token": str(self.api_key).strip(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "model": "RD_FLUX",
                "width": 512,
                "height": 512,
                "prompt": prompt,
                "num_images": 1
            }

            async with ctx.typing():
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30  # Add timeout
                )
                
                # Log the request details (excluding API key)
                log_headers = headers.copy()
                log_headers["X-RD-Token"] = "REDACTED"
                log_error(f"RetroAI Request - URL: {self.api_url}, Headers: {log_headers}, Payload: {payload}")
                
                response.raise_for_status()
            
            # Process the response
            result = response.json()
            if "base64_images" in result and len(result["base64_images"]) > 0:
                # Decode the base64 image
                img_data = base64.b64decode(result["base64_images"][0])
                
                # Ensure the directory exists
                os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
                
                # Save the image temporarily
                image_path = os.path.join(GENERATED_IMAGES_DIR, f"retro_{ctx.message.id}.png")
                with open(image_path, 'wb') as file:
                    file.write(img_data)
                
                # Send info about the generation
                embed = discord.Embed(
                    title="🎨 RetroAI Image Generation",
                    description=f"**Prompt:** {prompt}",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Model", value=result.get("model", "RD_FLUX"), inline=True)
                embed.add_field(name="Credit Cost", value=result.get("credit_cost", "1"), inline=True)
                embed.add_field(name="Remaining Credits", value=result.get("remaining_credits", "N/A"), inline=True)
                
                # Delete the status message and send the result
                await status_message.delete()
                await ctx.send(embed=embed, file=discord.File(image_path))
                
                # Clean up the temporary file
                try:
                    os.remove(image_path)
                except Exception as e:
                    log_error(f"Error cleaning up temporary file: {str(e)}")
            else:
                await status_message.edit(content="❌ No images were generated in the response.")
            
        except requests.exceptions.HTTPError as http_err:
            error_msg = "❌ HTTP error occurred"
            try:
                error_details = response.json()
                if 'detail' in error_details:
                    if isinstance(error_details['detail'], list):
                        # Handle validation errors
                        errors = [f"{e['msg']} ({'.'.join(map(str, e['loc']))})" for e in error_details['detail']]
                        error_msg = f"{error_msg}: {'; '.join(errors)}"
                    else:
                        error_msg = f"{error_msg}: {error_details['detail']}"
            except Exception:
                error_msg = f"{error_msg}: {str(http_err)}"
            
            await status_message.edit(content=error_msg)
            log_error(f"RetroAI HTTP error: {str(http_err)}. Response: {response.text}")
            
        except requests.exceptions.Timeout:
            await status_message.edit(content="❌ Request timed out. Please try again.")
            log_error("RetroAI request timed out")
            
        except requests.exceptions.RequestException as e:
            await status_message.edit(content=f"❌ Network error occurred: {str(e)}")
            log_error(f"RetroAI request error: {str(e)}")
            
        except Exception as e:
            await status_message.edit(content=f"❌ An unexpected error occurred: {str(e)}")
            log_error(f"RetroAI unexpected error: {str(e)}")

    @commands.command(name='retro_models', help="Lists available RetroAI models")
    async def list_models(self, ctx):
        """Display information about available RetroAI models"""
        embed = discord.Embed(
            title="🎨 Available RetroAI Models",
            description="Here are the available models for image generation:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="RD_FLUX",
            value="Standard retro-style image generation model\n"
                  "• Resolution: Up to 512x512\n"
                  "• Best for: Retro-style artwork and illustrations",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='retro_debug', help="Debug RetroAI configuration (Admin only)")
    @commands.has_permissions(administrator=True)
    async def debug_config(self, ctx):
        """Debug RetroAI configuration (Admin only)"""
        # Redact most of the API key but show the last 4 characters
        if self.api_key:
            visible_key = f"{'*' * (len(self.api_key)-4)}{self.api_key[-4:]}"
            key_length = len(self.api_key)
            key_status = f"✅ Set (Length: {key_length} chars)"
        else:
            visible_key = "Not set"
            key_status = "❌ Not Set"
            
        embed = discord.Embed(
            title="🔧 RetroAI Debug Information",
            color=discord.Color.orange()
        )
        embed.add_field(name="API Key Status", value=key_status, inline=True)
        embed.add_field(name="API Key Preview", value=visible_key, inline=True)
        embed.add_field(name="API URL", value=self.api_url, inline=False)
        
        # Add environment check
        env_key = os.getenv('RETRODIFF_API')
        env_status = "✅ Found in .env" if env_key else "❌ Not found in .env"
        embed.add_field(name="Environment Check", value=env_status, inline=True)
        
        # Add config check
        config_key = RETRO_API_KEY
        config_status = "✅ Found in config" if config_key else "❌ Not found in config"
        embed.add_field(name="Config Check", value=config_status, inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RetroDiffusion(bot)) 