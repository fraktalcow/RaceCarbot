import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
DISCORD_TOKEN = os.getenv('APIKEY')
GEMINI_API_KEY = os.getenv('GEMINI_API')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
RETRO_API_KEY = os.getenv('RETRODIFF_API')

# API Endpoints
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
RETRO_API_URL = "https://api.retrodiffusion.ai/v1/inferences"

# Bot Settings
BOT_PREFIX = '!'
DEFAULT_EMOJIS = ['⏳', '🔥', '✨', '🕑', '🤖', '💡', '🌟', '⚙️', '🌀', '🚀']

# File Paths
GENERATED_IMAGES_DIR = "generated_images"
LOG_DIR = "logs"
ERROR_LOG = "error_log.txt"
MESSAGE_LOG = "message_log.csv"
BOT_LOG = "bot.log" 