from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.database import AsyncSessionLocal
from database.crud import UserCRUD
from config import config
from bot.keyboards.inline import get_main_reply_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("auth"))
async def auth_handler(message: Message):
    """Обработчик авторизации"""
    try:
        # Проверяем формат команды
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Используйте: <code>/auth ВАШ_КОД</code>",
                parse_mode="HTML"
            )
            return
        
        auth_code = command_parts[1]
        
        # Проверяем код авторизации
        if auth_code not in config.AUTH_CODES:
            await message.answer("❌ Неверный код авторизации.")
            return
        
        # Получаем имя пользователя по коду
        user_name = config.AUTH_CODES[auth_code]
        
        async with AsyncSessionLocal() as db:
            # Проверяем, не авторизован ли уже пользователь
            existing_user = await UserCRUD.get_user_by_telegram_id(db, message.from_user.id)
            
            if existing_user and existing_user.is_authorized:
                await message.answer("✅ Вы уже авторизованы в системе.")
                return
            
            # Создаем нового пользователя или обновляем существующего
            if not existing_user:
                user = await UserCRUD.create_user(
                    db=db,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username or "",
                    full_name=user_name,
                    auth_code=auth_code
                )
            else:
                existing_user.is_authorized = True
                existing_user.auth_code = auth_code
                existing_user.full_name = user_name
                await db.commit()
                user = existing_user
            
            success_text = (
                f"✅ <b>Авторизация успешна!</b>\n\n"
                f"👤 Добро пожаловать, <b>{user.full_name}</b>\n\n"
                f"🤖 Теперь вы можете пользоваться ботом.\n"
                f"Напишите любое сообщение для вызова главного меню."
            )
            
            await message.answer(success_text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())
            logger.info("User authorized successfully")
    
    except Exception as e:
        logger.error(f"Authorization error: {e}")
        await message.answer("❌ Произошла ошибка при авторизации. Попробуйте позже.")