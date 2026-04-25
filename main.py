import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, TypeHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import BOT_TOKEN, LOCAL_API_URL, READ_TIMEOUT, WRITE_TIMEOUT, CONNECT_TIMEOUT, POOL_TIMEOUT
from bot.server import keep_alive
from bot.handlers.commands import start_cmd
from bot.handlers.admin import add_group_cmd, remove_group_cmd, groups_cmd
from bot.handlers.muxer import process_document, process_video, cancel_task_callback

nest_asyncio.apply()

# --- ANTI-CRASH: DUPLICATE UPDATE PREVENTER ---
PROCESSED_UPDATES = set()

async def duplicate_blocker(update: Update, context):
    if update.update_id in PROCESSED_UPDATES:
        raise ApplicationHandlerStop() # Drops the duplicate update safely
    PROCESSED_UPDATES.add(update.update_id)
    if len(PROCESSED_UPDATES) > 5000:
        PROCESSED_UPDATES.pop() # Prevent memory leak

def main():
    # Render Health Check Bypass Start
    keep_alive()

    # Local API & Timeout Optimizations setup
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .base_url(LOCAL_API_URL)
        .local_mode(True)
        .read_timeout(READ_TIMEOUT)
        .write_timeout(WRITE_TIMEOUT)
        .connect_timeout(CONNECT_TIMEOUT)
        .pool_timeout(POOL_TIMEOUT)
        .concurrent_updates(True)
        .build()
    )

    # Handlers Registration
    app.add_handler(TypeHandler(Update, duplicate_blocker), group=-1)
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("addgroup", add_group_cmd))
    app.add_handler(CommandHandler("removegroup", remove_group_cmd))
    app.add_handler(CommandHandler("groups", groups_cmd))

    app.add_handler(MessageHandler(filters.VIDEO, process_video))
    app.add_handler(MessageHandler(filters.Document.ALL, process_document))
    
    app.add_handler(CallbackQueryHandler(cancel_task_callback, pattern="^cancel_"))

    print("🚀 Enterprise Bot is running with Local API & FFmpeg...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
