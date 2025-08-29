from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.types import Message
from services.analytics import analytics_service
from bot.keyboards.inline import get_analytics_keyboard, get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("analytics"))
async def analytics_command(message: Message, current_user):
    """Команда для вызова аналитики"""
    keyboard = get_analytics_keyboard()
    
    summary = await analytics_service.get_analytics_summary()
    
    text = f"{summary}\n\n🎯 Выберите тип аналитики:"
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    logger.info(f"Analytics menu opened by user {current_user.full_name}")

@router.callback_query(F.data == "analytics")
async def show_analytics_menu(callback: CallbackQuery, current_user):
    """Показать меню аналитики"""
    keyboard = get_analytics_keyboard()
    
    summary = await analytics_service.get_analytics_summary()
    
    text = f"{summary}\n\n🎯 Выберите тип аналитики:"
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()
    logger.info(f"Analytics menu shown to user {current_user.full_name}")

@router.callback_query(F.data.startswith("chart_"))
async def generate_chart(callback: CallbackQuery, current_user):
    """Генерация и отправка графиков"""
    try:
        chart_type = callback.data.split("_")[1]
        days = int(callback.data.split("_")[2]) if len(callback.data.split("_")) > 2 else 30
        
        # Показываем индикатор загрузки
        await callback.answer("📊 Генерирую график...", show_alert=False)
        
        # Генерируем график в зависимости от типа
        if chart_type == "trend":
            img_buffer = await analytics_service.generate_daily_trend_chart(days)
            caption = f"📈 Динамика расходов за последние {days} дней"
            
        elif chart_type == "pie":
            img_buffer = await analytics_service.generate_user_pie_chart(days)
            caption = f"🍰 Распределение расходов по пользователям за {days} дней"
            
        elif chart_type == "comparison":
            img_buffer = await analytics_service.generate_user_comparison_chart(days)
            caption = f"📊 Сравнение активности пользователей за {days} дней"
            
        elif chart_type == "weekly":
            img_buffer = await analytics_service.generate_weekly_summary_chart()
            caption = "📅 Недельная сводка расходов"
            
        elif chart_type == "category":
            img_buffer = await analytics_service.generate_category_pie_chart(days)
            caption = f"📊 Расходы по категориям за {days} дней"
            
        else:
            await callback.message.answer("❌ Неизвестный тип графика")
            return
        
        # Создаем BufferedInputFile из BytesIO
        photo = BufferedInputFile(
            img_buffer.getvalue(),
            filename=f"{chart_type}_{days}days.png"
        )
        
        # Отправляем изображение
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=get_analytics_keyboard()
        )
        
        logger.info(f"Chart {chart_type} generated for user {current_user.full_name}")
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        await callback.message.answer(
            "❌ Ошибка при создании графика. Попробуйте позже.",
            reply_markup=get_analytics_keyboard()
        )
        await callback.answer()

@router.callback_query(F.data.startswith("summary_"))
async def show_analytics_summary(callback: CallbackQuery, current_user):
    """Показать текстовую сводку аналитики"""
    try:
        days = int(callback.data.split("_")[1])
        
        await callback.answer("📊 Формирую отчет...", show_alert=False)
        
        summary = await analytics_service.get_analytics_summary(days)
        
        keyboard = get_analytics_keyboard()
        
        await callback.message.edit_text(
            summary,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        logger.info(f"Analytics summary ({days} days) shown to user {current_user.full_name}")
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        await callback.message.answer(
            "❌ Ошибка при создании отчета. Попробуйте позже.",
            reply_markup=get_analytics_keyboard()
        )
        await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    text = (
        "🏠 <b>Главное меню</b>\n\n"
        "Добро пожаловать в систему учета финансов!\n"
        "Выберите необходимое действие:"
    )
    
    keyboard = get_main_menu_keyboard()
    
    # Fix: Handle photo messages that can't be edited with text
    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        # If editing fails (e.g., photo message), send new message
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    await callback.answer()

@router.message(Command("sync"))
async def sync_data_command(message: Message, current_user):
    """Команда для синхронизации данных с Google Sheets"""
    from services.google_sheets import google_sheets_service
    
    await message.answer("🔄 Начинаю синхронизацию с Google Sheets...")
    
    try:
        await google_sheets_service.sync_expenses_from_sheets()
        await message.answer("✅ Синхронизация завершена!\n\nДанные из Google Sheets загружены в локальную базу.")
        
        logger.info("Data sync completed successfully")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        await message.answer("❌ Ошибка при синхронизации. Проверьте подключение к Google Sheets.")

