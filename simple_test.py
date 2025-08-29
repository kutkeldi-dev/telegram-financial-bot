import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8311452814:AAEV5MN3oVK88YFAhrMFTTCs0TCUFtuW7Z8"

# Простейший тест бота
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Hello! Bot is working!")

@dp.message()  
async def echo(message: types.Message):
    await message.answer(f"You said: {message.text}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Simple bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())