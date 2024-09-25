import os

import aiohttp
from aiohttp import FormData

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def send_to_telegram_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                print("Text message sent to Telegram bot successfully.")
            else:
                print(f"Failed to send text message: {response.status}")


async def send_to_telegram_file(file_content, file_name):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    form_data = FormData()
    form_data.add_field("chat_id", CHAT_ID)
    form_data.add_field("document", file_content, filename=file_name)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            if response.status == 200:
                print("File sent to Telegram bot successfully.")
            else:
                print(f"Failed to send file: {response.status}")
