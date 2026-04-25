from telegram import Update
from telegram.ext import ContextTypes
from bot.auth import is_owner, ALLOWED_GROUPS

async def add_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("⛔ You are not the bot owner.")
    
    chat_id = update.effective_chat.id
    ALLOWED_GROUPS.add(chat_id)
    await update.message.reply_text(f"✅ Group {chat_id} added to Whitelist!")

async def remove_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("⛔ You are not the bot owner.")
    
    chat_id = update.effective_chat.id
    if chat_id in ALLOWED_GROUPS:
        ALLOWED_GROUPS.remove(chat_id)
        await update.message.reply_text(f"❌ Group {chat_id} removed from Whitelist!")
    else:
        await update.message.reply_text("Group is not in whitelist.")

async def groups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(f"📁 **Allowed Groups:**\n{list(ALLOWED_GROUPS)}", parse_mode="Markdown")
