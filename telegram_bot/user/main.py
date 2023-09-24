from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, Message, InputMediaPhoto
from pyrogram.enums.parse_mode import ParseMode
import asyncio
from modules.integrations.notes import get_telegram_message


app = Client("forgenet", api_id=21689012, api_hash="cf3421f4d8bc3fa257ac934d7184984c")


@app.on_message(filters.command("schedule"))
async def resize(client: Client, message: Message):
    await client.send_message(message.chat.id, get_telegram_message("М3О-121Б-23", 4), parse_mode=ParseMode.MARKDOWN)

app.run()
