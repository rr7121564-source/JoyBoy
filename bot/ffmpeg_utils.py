import asyncio
import time

async def run_muxer(video_path: str, sub_path: str, font_path: str, output_path: str, message, user_id, active_tasks):
    """Executes FFmpeg safely in background with cancel listener and progress."""
    
    sub_ext = sub_path.split('.')[-1].lower()
    sub_codec = "ass" if sub_ext == "ass" else "srt"
    
    # FFmpeg Command Structure:
    # -map 0:v -map 0:a : Video & Audio Copy (Original subtitles delete ho jayenge)
    # -map 1 : Naya subtitle inject karega
    # -disposition:s:0 default : Naye sub ko default play karega
    # -attach : Local Font attach karega
    cmd =[
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", sub_path,
        "-map", "0:v", "-map", "0:a", "-map", "1",
        "-c:v", "copy", "-c:a", "copy",
        "-c:s", sub_codec,
        "-disposition:s:0", "default",
        "-attach", font_path,
        "-metadata:s:t", "mimetype=application/x-truetype-font",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Save process reference for Cancellation
    active_tasks[user_id] = process

    # Update Progress Loop
    last_update = time.time()
    try:
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            
            # Progress update in bot message (Rate limit protected)
            if time.time() - last_update > 5:
                await message.edit_text(
                    f"⚙️ **Processing MKV...**\n\n"
                    f"Removing old subs, injecting '{sub_ext.upper()}' as default and attaching Font from GitHub Repository.\n"
                    f"Please wait...", 
                    parse_mode='Markdown'
                )
                last_update = time.time()

        await process.wait()
    except asyncio.CancelledError:
        process.kill()
        raise

    if process.returncode != 0:
        raise Exception("FFmpeg failed to process the file.")
