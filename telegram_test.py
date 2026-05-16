from telegram import Bot
import asyncio

TOKEN = "8811806530:AAGLledqz3X-V6FimzqYfntERMwUy_D2Jas"
CHAT_ID = "6610857554"

async def send_message():
    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="🔥 AI Meeting Guardian Activated"
    )

asyncio.run(send_message())