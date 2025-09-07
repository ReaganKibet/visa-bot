# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

VFS_TARGET_URL = os.getenv("VFS_TARGET_URL")