import asyncio
import logging
from aiogram import Bot

# Простой тест подключения к боту
async def test_bot():
    BOT_TOKEN = "8311452814:AAEV5MN3oVK88YFAhrMFTTCs0TCUFtuW7Z8"
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Проверяем информацию о боте
        bot_info = await bot.get_me()
        print("Bot connected successfully!")
        print(f"Bot username: @{bot_info.username}")
        print(f"Bot name: {bot_info.first_name}")
        print(f"Bot ID: {bot_info.id}")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())