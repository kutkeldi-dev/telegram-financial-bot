from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import UserCRUD

class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации пользователя"""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем команды авторизации и старта
        if isinstance(event, Message):
            if event.text and (event.text.startswith('/auth') or event.text.startswith('/start')):
                return await handler(event, data)
        
        # Проверяем авторизацию
        async with AsyncSessionLocal() as db:
            user = await UserCRUD.get_user_by_telegram_id(db, event.from_user.id)
            
            if not user or not user.is_authorized:
                await event.answer("❌ Вы не авторизованы. Используйте команду /auth [код]")
                return
            
            data['current_user'] = user
            return await handler(event, data)