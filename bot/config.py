import os

# Telegram Settings
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8588606800:AAGDQZpPNCCrCKtslaP-Hp5k_r3ZAj4t5js")
OWNER_ID = int(os.environ.get("OWNER_ID", "6751462767")) # Apni Telegram User ID daalein

# Local API Settings (Mandatory Rule)
LOCAL_API_URL = os.environ.get("LOCAL_API_URL", "http://127.0.0.1:8081/bot")

# NAYA: Local Font ka path (Jo GitHub repo me 'fonts' folder me hoga)
# Aap apne font ka exact naam yaha likhein 'custom_font.ttf' ki jagah
LOCAL_FONT_PATH = os.environ.get("LOCAL_FONT_PATH", "fonts/custom_font.ttf")

# Timeouts
READ_TIMEOUT = 3600
WRITE_TIMEOUT = 3600
CONNECT_TIMEOUT = 100
POOL_TIMEOUT = 100
