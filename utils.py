import os
import logging
import random
from datetime import datetime
import csv
from config import *

# Setup logging
def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, BOT_LOG),
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

# Log message to CSV
def log_message(message_id, author_name, content):
    with open(MESSAGE_LOG, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([message_id, author_name, content, datetime.now()])

# React with random emoji
async def react_with_random_emoji(message):
    emoji = random.choice(DEFAULT_EMOJIS)
    await message.add_reaction(emoji)

# Ensure directories exist
def ensure_directories():
    directories = [GENERATED_IMAGES_DIR, LOG_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Error logging
def log_error(error):
    logging.error(f"An error occurred: {str(error)}")
    with open(os.path.join(LOG_DIR, ERROR_LOG), 'a') as f:
        f.write(f"{datetime.now()}: {str(error)}\n") 