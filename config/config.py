import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'MTIwOTg3NTcxMjk5NjI4NjU4NQ.GRNVJY.MqgkgbOXsFKfqAsHYA0G6zNXgcDInnrB-PZ4_M')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://barshan2004:Bmtargetis100@ezproject.ohetccl.mongodb.net/?retryWrites=true&w=majority&appName=EzProject')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'discord')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'tasks')

# Bot Settings
BOT_NAME = "EzProject Bot"
BOT_DESCRIPTION = "A bot that facilitates group projects by assigning tasks, tracking progress, and enabling seamless communication within the team."

# Colors for embeds
EMBED_COLORS = {
    'success': 0x00ff00,  # Green
    'error': 0xff0000,    # Red
    'info': 0x0099ff,     # Blue
    'warning': 0xffaa00,  # Orange
    'purple': 0x9932cc    # Purple
}

# Task status emojis
STATUS_EMOJIS = {
    'complete': '✅',
    'incomplete': '❌',
    'in_progress': '🔄',
    'pending': '⏳'
} 