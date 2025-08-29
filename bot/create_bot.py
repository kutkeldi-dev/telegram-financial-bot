from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import config
from bot.middlewares.auth import AuthMiddleware
from bot.handlers import auth, common, expenses, status, instructions, analytics

def create_bot() -> tuple[Bot, Dispatcher]:
    """Создание экземпляра бота и диспетчера"""
    
    # Создаем бота
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаем диспетчер
    dp = Dispatcher()
    
    # Регистрируем middleware (авторизация НЕ для auth и start команд)
    auth_middleware = AuthMiddleware()
    
    # Регистрируем роутеры
    dp.include_router(auth.router)      # Авторизация (без middleware)
    
    # Остальные роутеры с middleware
    expenses.router.message.middleware(auth_middleware)
    expenses.router.callback_query.middleware(auth_middleware)
    
    status.router.callback_query.middleware(auth_middleware)
    instructions.router.callback_query.middleware(auth_middleware)
    
    analytics.router.message.middleware(auth_middleware)
    analytics.router.callback_query.middleware(auth_middleware)
    
    common.router.message.middleware(auth_middleware)
    common.router.callback_query.middleware(auth_middleware)
    
    dp.include_router(expenses.router)
    dp.include_router(status.router)  
    dp.include_router(analytics.router)
    dp.include_router(instructions.router)
    dp.include_router(common.router)    # В конце, как fallback
    
    return bot, dp