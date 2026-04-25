import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.auth import is_allowed_chat, is_owner
from bot.ffmpeg_utils import run_muxer
from bot.config import LOCAL_FONT_PATH

USER_LOCKS = {}
ACTIVE_TASKS = {}
QUEUE_LOCK = asyncio.Lock()

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_chat(update.effective_chat.id):
        return
    
    video = update.message.video or update.message.document
    if not video.file_name.lower().endswith('.mkv'):
        return await update.message.reply_text("⚠️ Please send an `.mkv` file.")

    # Using Local API path directly! No RAM loading.
    file_obj = await context.bot.get_file(video.file_id)
    context.user_data['video_path'] = file_obj.file_path
    
    await update.message.reply_text("✅ MKV Video saved in memory.\n\nNow send the Subtitle File (`.srt` or `.ass`).")

async def process_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_chat(update.effective_chat.id):
        return
    
    doc = update.message.document
    if doc.file_name.lower().endswith(('.mkv', '.mp4')):
        return await process_video(update, context)

    if not doc.file_name.lower().endswith(('.srt', '.ass')):
        return await update.message.reply_text("⚠️ Only `.srt` and `.ass` subtitles are supported.")

    if 'video_path' not in context.user_data:
        return await update.message.reply_text("⚠️ Please send the MKV Video FIRST.")

    user_id = update.effective_user.id
    
    # User queue lock logic
    if user_id not in USER_LOCKS:
        USER_LOCKS[user_id] = asyncio.Lock()
    
    if USER_LOCKS[user_id].locked():
        return await update.message.reply_text("⏳ You already have a task running. Please wait in queue!")

    async with USER_LOCKS[user_id]:
        await execute_muxing(update, context, doc)

async def execute_muxing(update: Update, context: ContextTypes.DEFAULT_TYPE, sub_doc):
    user_id = update.effective_user.id
    video_path = context.user_data['video_path']
    
    # Check if Local Font exists
    font_path = LOCAL_FONT_PATH
    if not os.path.exists(font_path):
        return await update.message.reply_text(
            f"❌ **Font File Missing!**\n\nBot ke server pe '{font_path}' nahi mila. Kripya GitHub repo me 'fonts' folder banayein aur font upload karein.", 
            parse_mode="Markdown"
        )
    
    # Get Subtitle Path
    sub_file = await context.bot.get_file(sub_doc.file_id)
    sub_path = sub_file.file_path
    
    output_path = os.path.join(os.path.dirname(video_path), f"softsub_{user_id}_{os.path.basename(video_path)}")

    cancel_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🚫 Cancel Task", callback_data=f"cancel_{user_id}")]])
    status_msg = await update.message.reply_text("⚙️ **Muxing Started...**", reply_markup=cancel_markup, parse_mode="Markdown")

    try:
        # Async Muxing Execution (Queue Management System)
        async with QUEUE_LOCK:
            task = asyncio.create_task(run_muxer(video_path, sub_path, font_path, output_path, status_msg, user_id, ACTIVE_TASKS))
            await task
        
        # Uploading back using file:// protocol
        await status_msg.edit_text("🚀 **Uploading MKV File...**", parse_mode="Markdown")
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f"file://{output_path}",
            caption="✅ **File Successfully Muxed!**\n- Old subs deleted\n- New sub is Default\n- Attached Repo's Local Font.",
            parse_mode="Markdown"
        )
        
    except asyncio.CancelledError:
        await status_msg.edit_text("❌ Task Cancelled by User.")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error occurred: {str(e)}")
    finally:
        # Guaranteed Cleanup (We DO NOT delete the local font anymore, only output path and video)
        context.user_data.pop('video_path', None)
        ACTIVE_TASKS.pop(user_id, None)
        
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

async def cancel_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = int(query.data.split("_")[1])
    
    if update.effective_user.id != user_id and not is_owner(update.effective_user.id):
        return await query.answer("You cannot cancel this task!", show_alert=True)
    
    process = ACTIVE_TASKS.get(user_id)
    if process:
        process.kill()
        await query.answer("Task Killed!", show_alert=True)
    else:
        await query.answer("No active task found.", show_alert=True)
