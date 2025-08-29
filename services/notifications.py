from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def send_daily_reminder(self, telegram_id: int):
        """Отправка ежедневного напоминания в 20:00"""
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 Добавить расход", callback_data="expense")],
                [InlineKeyboardButton(text="📊 Посмотреть статус", callback_data="status")]
            ])
            
            message = (
                "🕐 <b>Ежедневное напоминание</b>\n\n"
                "Пожалуйста, укажите ваши расходы за сегодня.\n"
                "Если расходов не было - нажмите на кнопку и укажите 0.\n\n"
                "📝 Это поможет вести точный учет финансов бизнеса."
            )
            
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            
            logger.info(f"Daily reminder sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending daily reminder to user {telegram_id}: {e}")
    
    async def send_hourly_reminder(self, telegram_id: int, reminder_count: int):
        """Отправка почасового напоминания"""
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 Добавить расход сейчас", callback_data="expense")]
            ])
            
            message = (
                f"⏰ <b>Напоминание #{reminder_count}</b>\n\n"
                "Вы еще не указали расходы за сегодня.\n"
                "Пожалуйста, внесите информацию о тратах.\n\n"
                "💡 Если расходов не было, укажите сумму 0."
            )
            
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode="HTML", 
                reply_markup=keyboard
            )
            
            logger.info(f"Hourly reminder #{reminder_count} sent to user {telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending hourly reminder to user {telegram_id}: {e}")