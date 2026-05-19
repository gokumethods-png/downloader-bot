import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
import yt_dlp

# Setup Configuration & Logging
BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"

logging.basicConfig(level=logging.INFO)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_video(url: str) -> str:
    """
    Downloads video using yt-dlp configured for Telegram bot limits.
    """
    outtmpl = os.path.join(DOWNLOAD_DIR, '%(title).50s.%(ext)s')

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'restrictfilenames': True,
        'noplaylist': True,
        'max_filesize': 50 * 1024 * 1024,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "👋 Welcome to the Video Downloader Bot!\n\n"
        "Send me a video link from YouTube, TikTok, Instagram Reels, or Twitter."
    )

@dp.message(F.text.startswith("http://") | F.text.startswith("https://"))
async def handle_video_link(message: Message):
    url = message.text.strip()

    status_msg = await message.reply(
        "⏳ Processing link and downloading video..."
    )

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(
            None,
            download_video,
            url
        )

        if os.path.exists(file_path):
            await status_msg.edit_text(
                "🚀 Uploading video to Telegram..."
            )

            from aiogram.types import FSInputFile

            video_file = FSInputFile(file_path)

            await message.reply_video(
                video=video_file,
                caption="Downloaded via your Bot! 📥"
            )

            os.remove(file_path)
            await status_msg.delete()

        else:
            await status_msg.edit_text(
                "❌ Failed to locate downloaded file."
            )

    except yt_dlp.utils.MaxFileSizeReachedError:
        await status_msg.edit_text(
            "❌ File exceeds 50MB Telegram limit."
        )

    except Exception as e:
        logging.error(f"Download Error: {e}")

        await status_msg.edit_text(
            "❌ Couldn't download that video."
        )

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
