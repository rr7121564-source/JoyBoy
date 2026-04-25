from telegram import Update
from telegram.ext import ContextTypes
from bot.auth import is_allowed_chat

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_chat(update.effective_chat.id):
        return await update.message.reply_text("⛔ Unauthorized Access. Ask Owner to whitelist this chat.")
    
    text = (
        "🎬 **Welcome to Ultra-Fast SoftSub Bot!**\n\n"
        "1️⃣ Send an `MKV` Video.\n"
        "2️⃣ Send a Subtitle (`SRT` / `ASS`).\n\n"
        "⚡ I will remove old subs, embed the new sub as DEFAULT, fetch font from GitHub and attach it to the MKV!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
