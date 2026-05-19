from flask import Flask
from threading import Thread
import os

# ---------------- KEEP BOT ALIVE FOR RENDER ---------------- #

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# ---------------- YOUR TELEGRAM BOT CODE BELOW ---------------- #

import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
import yt_dlp

# 1. Setup Configuration & Logging
BOT_TOKEN = "8989462164:AAHbMsOUdx8OgHbt5raW_bsbNruEA8pHV0Q"  # <-- Put your BotFather token here
DOWNLOAD_DIR = "downloads"

logging.basicConfig(level=logging.INFO)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 2. Function to extract and download the video using yt-dlp
def download_video(url: str) -> str:
    """
    Downloads video using yt-dlp configured for typical Telegram bot constraints.
    Limits downloads to ~50MB to match Telegram's standard bot upload threshold.
    """
    outtmpl = os.path.join(DOWNLOAD_DIR, '%(title).50s.%(ext)s')
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Prefers MP4 containers for native TG playback
        'outtmpl': outtmpl,
        'restrictfilenames': True,
        'noplaylist': True,
        # Restrict filesize roughly under 50MB so standard bots can send it over HTTP API
        'max_filesize': 50 * 1024 * 1024, 
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# 3. Command Handlers
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "👋 **Welcome to the Video Downloader Bot!**\n\n"
        "Just send me a video link from YouTube, TikTok, Instagram Reels, or Twitter, "
        "and I will try to extract the file and send it to you."
    )

@dp.message(F.text.startswith("http://") | F.text.startswith("https://"))
async def handle_video_link(message: Message):
    url = message.text.strip()
    status_msg = await message.reply("⏳ *Processing link and downloading video... Please wait.*", parse_mode="Markdown")
    
    try:
        # Run the synchronous yt-dlp downloader in a separate thread so it doesn't freeze the bot
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_video, url)
        
        if os.path.exists(file_path):
            await status_msg.edit_text("🚀 *Uploading video to Telegram...*", parse_mode="Markdown")
            
            # Send video to user
            from aiogram.types import FSInputFile
            video_file = FSInputFile(file_path)
            await message.reply_video(video=video_file, caption="Downloaded via your Bot! 📥")
            
            # Clean up disk space
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Failed to parse or locate the downloaded file.")
            
    except yt_dlp.utils.MaxFileSizeReachedError:
        await status_msg.edit_text("❌ **Error:** File size exceeds the standard 50MB limit allowed for basic Telegram bots.")
    except Exception as e:
        logging.error(f"Download Error: {e}")
        await status_msg.edit_text("❌ Sorry, I couldn't download that video. Check if the link is correct or public.")

# 4. Main execution loop
async def main():
    print("Bot is up and running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
