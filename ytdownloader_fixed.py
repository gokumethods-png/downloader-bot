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

# Example:
# from aiogram import Bot, Dispatcher
# import asyncio
#
# TOKEN = "YOUR_BOT_TOKEN"
#
# async def main():
#     bot = Bot(token=TOKEN)
#     dp = Dispatcher()
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())
