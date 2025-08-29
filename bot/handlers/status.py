from aiogram import Router, F
from aiogram.types import CallbackQuery
from services.google_sheets import google_sheets_service
from bot.keyboards.inline import get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

async def show_status_data(message_or_callback, current_user):
    """Общая функция для показа статуса"""
    """Показать статус финансов"""
    try:
        # Получаем данные из Google Sheets
        status_data = await google_sheets_service.get_status_data()
        
        if not status_data:
            error_text = (
                "❌ Не удалось получить данные статуса.\n"
                "Проверьте настройки Google Sheets."
            )
            
            # Определяем тип объекта и отправляем соответственно
            if hasattr(message_or_callback, 'answer') and hasattr(message_or_callback, 'message'):
                # Это CallbackQuery
                await message_or_callback.message.edit_text(error_text, reply_markup=get_main_menu_keyboard())
                await message_or_callback.answer()
            else:
                # Это Message
                from bot.keyboards.inline import get_main_reply_keyboard
                await message_or_callback.answer(error_text, reply_markup=get_main_reply_keyboard())
            return
        
        # Получаем значения или устанавливаем по умолчанию 0
        total_turnover = status_data.get('Общий оборот', 0)
        product_costs = status_data.get('Затраты на товар', 0)  
        personal_expenses = status_data.get('Личные затраты', 0)
        business_investment = status_data.get('Инвестиции в бизнес', 0)
        shop1_account = status_data.get('Счет ISKO.TOOLS', 0)
        shop2_account = status_data.get('Счет TANKER', 0)
        account_balance = status_data.get('Остаток в счете', 0)
        
        # Вычисляем общие суммы
        total_bank_deposits = shop1_account + shop2_account
        
        # Формируем сообщение статуса
        status_text = (
            f"📊 <b>Финансовый статус</b>\n"
            f"👤 Запросил: {current_user.full_name}\n\n"
            
            f"💰 <b>1. Общий оборот:</b>\n"
            f"   {total_turnover:,.2f} сом\n\n"
            
            f"📦 <b>2. Затраты на товар:</b>\n" 
            f"   {product_costs:,.2f} сом\n\n"
            
            f"👤 <b>3. Личные затраты:</b>\n"
            f"   {personal_expenses:,.2f} сом\n\n"
            
            f"🏦 <b>4. Поступило в банк:</b>\n"
            f"   • Счет ISKO.TOOLS: {shop1_account:,.2f} сом\n"
            f"   • Счет TANKER: {shop2_account:,.2f} сом\n\n"
            
            f"💳 <b>5. Остаток в счете:</b>\n"
            f"   {account_balance:,.2f} сом\n\n"
            
            f"📋 <b>Общие суммы:</b>\n"
            f"• Всего оборот: {total_turnover:,.2f} сом\n"
            f"• Затраты на товар: {product_costs:,.2f} сом\n"
            f"• Поступило денег в банк: {total_bank_deposits:,.2f} сом\n\n"
            
            f"🕐 <i>Данные из Google Таблицы</i>"
        )
        
        # Определяем тип объекта и отправляем соответственно
        if hasattr(message_or_callback, 'answer') and hasattr(message_or_callback, 'message'):
            # Это CallbackQuery
            keyboard = get_main_menu_keyboard()
            try:
                await message_or_callback.message.edit_text(
                    status_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception:
                # Если не можем редактировать, отправляем новое сообщение
                await message_or_callback.message.answer(
                    status_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            await message_or_callback.answer()
        else:
            # Это Message
            from bot.keyboards.inline import get_main_reply_keyboard
            keyboard = get_main_reply_keyboard()
            await message_or_callback.answer(
                status_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        
        logger.info("Status data requested successfully")
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        error_text = (
            "❌ Произошла ошибка при получении статуса.\n"
            "Попробуйте позже или обратитесь к администратору."
        )
        
        # Определяем тип объекта и отправляем соответственно
        if hasattr(message_or_callback, 'answer') and hasattr(message_or_callback, 'message'):
            # Это CallbackQuery
            await message_or_callback.message.edit_text(error_text, reply_markup=get_main_menu_keyboard())
            await message_or_callback.answer()
        else:
            # Это Message
            from bot.keyboards.inline import get_main_reply_keyboard
            await message_or_callback.answer(error_text, reply_markup=get_main_reply_keyboard())

@router.callback_query(F.data == "status")
async def show_status(callback: CallbackQuery, current_user):
    """Обработчик кнопки статуса"""
    await show_status_data(callback, current_user)