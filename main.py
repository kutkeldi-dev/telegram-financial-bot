import asyncio
import logging
import sys
from bot.create_bot import create_bot
from database.database import create_tables
from services.scheduler import SchedulerService

# Настройка логирования с поддержкой UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix console encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    logger.info("Starting Telegram bot...")
    
    try:
        # Создаем таблицы в базе данных
        await create_tables()
        logger.info("Database initialized")
        
        # Создаем бота и диспетчер
        bot, dp = create_bot()
        logger.info("Bot created")
        
        # Выполняем начальную синхронизацию данных
        try:
            from services.google_sheets import google_sheets_service
            await google_sheets_service.sync_expenses_from_sheets()
            logger.info("Initial data sync completed")
        except Exception as e:
            logger.warning(f"Initial sync failed: {e}")
        
        # Создаем и запускаем планировщик
        scheduler = SchedulerService(bot)
        scheduler.start()
        logger.info("Scheduler started")
        
        # Запускаем polling
        logger.info("Bot is running and ready to work!")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        # Остановка планировщика при завершении
        if 'scheduler' in locals():
            scheduler.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())