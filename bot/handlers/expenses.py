from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from database.database import AsyncSessionLocal
from database.crud import ExpenseCRUD, ReminderCRUD
from services.google_sheets import google_sheets_service
from bot.states.expense import ExpenseForm
from bot.keyboards.inline import get_confirmation_keyboard, get_expense_completed_keyboard, get_category_selection_keyboard
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "expense")
async def start_expense_input(callback: CallbackQuery, state: FSMContext, current_user):
    """Начало процесса добавления расхода"""
    await state.set_state(ExpenseForm.waiting_amount)
    
    text = (
        f"💰 <b>Добавление расхода</b>\n\n"
        f"👤 Пользователь: <b>{current_user.full_name}</b>\n"
        f"📅 Дата: <b>{datetime.now().strftime('%d.%m.%Y')}</b>\n\n"
        f"💵 Введите сумму расхода (в сомах):\n"
        f"<i>Если расходов не было, введите 0</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.message(ExpenseForm.waiting_amount)
async def process_amount(message: Message, state: FSMContext, current_user):
    """Обработка суммы расхода"""
    try:
        # Clean and validate input
        amount_str = message.text.replace(',', '.').replace(' ', '').strip()
        amount = float(amount_str)
        
        if amount < 0:
            await message.answer("❌ Сумма не может быть отрицательной. Введите корректную сумму:")
            return
        
        if amount > 10000000:  # 10 million limit
            await message.answer("❌ Сумма слишком большая (максимум 10,000,000). Введите корректную сумму:")
            return
        
        # Check for reasonable decimal places
        if '.' in amount_str and len(amount_str.split('.')[1]) > 2:
            await message.answer("❌ Слишком много знаков после запятой (максимум 2). Введите корректную сумму:")
            return
        
        await state.update_data(amount=amount)
        await state.set_state(ExpenseForm.waiting_category)
        
        if amount == 0:
            # Для нулевых расходов сразу сохраняем без дополнительных вопросов
            try:
                async with AsyncSessionLocal() as db:
                    # Сохраняем расход в базу данных
                    expense = await ExpenseCRUD.create_expense(
                        db=db,
                        user_id=current_user.id,
                        amount=0.0,
                        purpose="Нет расходов",
                        category_name=None
                    )
                    
                    # Сохраняем в Google Sheets
                    await google_sheets_service.add_expense_to_sheet(
                        user_name=current_user.full_name,
                        amount=0.0,
                        purpose="Нет расходов",
                        expense_date=expense.created_at,
                        category=None
                    )
                    
                    # Отмечаем напоминание как выполненное
                    from datetime import date
                    from database.crud import ReminderCRUD
                    today = date.today()
                    pending_reminders = await ReminderCRUD.get_pending_reminders(db, today)
                    for reminder in pending_reminders:
                        if reminder.user_id == current_user.id:
                            await ReminderCRUD.mark_reminder_completed(db, reminder.id)
                            break
                
                success_text = (
                    f"✅ <b>Нулевой отчет сохранен!</b>\n\n"
                    f"📊 Записано: нет расходов за сегодня.\n\n"
                    f"Что дальше?"
                )
                
                await message.answer(
                    success_text,
                    parse_mode="HTML",
                    reply_markup=get_expense_completed_keyboard()
                )
                await state.clear()
                
                logger.info("Zero expense report saved successfully")
                return
                
            except Exception as e:
                logger.error(f"Error saving zero expense: {e}")
                await message.answer("❌ Произошла ошибка при сохранении. Попробуйте позже.")
                await state.clear()
                return
        else:
            # Для обычных расходов выбираем категорию
            category_text = (
                f"💰 Сумма: <b>{amount:,.2f} сом</b>\n\n"
                f"📂 <b>Выберите категорию расхода:</b>"
            )
            await message.answer(category_text, parse_mode="HTML", reply_markup=get_category_selection_keyboard())
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат суммы.\n"
            "Введите число (например: 1500 или 1500.50):"
        )

@router.callback_query(F.data.startswith("category_"), ExpenseForm.waiting_category)
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category_map = {
        "category_1": "Личные затраты",
        "category_2": "Жылдызбек ава", 
        "category_3": "Инвестиция",
        "category_4": "Услуга",
        "category_5": "Другое"
    }
    
    category_name = category_map.get(callback.data)
    if not category_name:
        await callback.answer("Ошибка выбора категории", show_alert=True)
        return
    
    await state.update_data(category=category_name)
    await state.set_state(ExpenseForm.waiting_purpose)
    
    data = await state.get_data()
    amount = data['amount']
    
    purpose_text = (
        f"💰 Сумма: <b>{amount:,.2f} сом</b>\n"
        f"📂 Категория: <b>{category_name}</b>\n\n"
        f"📝 <b>ВНИМАНИЕ! Сейчас введите ОПИСАНИЕ расхода (НЕ ЦИФРЫ!):</b>\n\n"
        f"Например:\n"
        f"• Покупка товара для магазина\n"
        f"• Оплата поставщику\n"
        f"• Транспортные расходы\n"
        f"• Личные нужды\n\n"
        f"❗ Введите ТЕКСТОМ, что именно покупали или на что тратили деньги"
    )
    
    await callback.message.edit_text(purpose_text, parse_mode="HTML")
    await callback.answer()

@router.message(ExpenseForm.waiting_purpose)
async def process_purpose(message: Message, state: FSMContext, current_user):
    """Обработка цели расхода"""
    purpose = message.text.strip()
    
    if not purpose:
        await message.answer("❌ Цель расхода не может быть пустой. Введите описание:")
        return
    
    # Проверяем, что пользователь не ввел только цифры
    if purpose.isdigit():
        await message.answer(
            "❌ Вы ввели только цифры!\n\n"
            "📝 Нужно ввести ОПИСАНИЕ расхода СЛОВАМИ:\n"
            "• Что покупали?\n"
            "• На что тратили деньги?\n"
            "• Для чего был расход?\n\n"
            "Например: 'Покупка продуктов', 'Оплата аренды', 'Транспорт'"
        )
        return
    
    if len(purpose) > 500:
        await message.answer("❌ Описание слишком длинное (максимум 500 символов). Сократите описание:")
        return
    
    data = await state.get_data()
    amount = data['amount']
    category = data.get('category', 'Не указана')
    
    await state.update_data(purpose=purpose)
    await state.set_state(ExpenseForm.waiting_confirmation)
    
    # Формируем сообщение подтверждения
    confirmation_text = (
        f"📋 <b>Подтверждение расхода</b>\n\n"
        f"👤 <b>Пользователь:</b> {current_user.full_name}\n"
        f"📅 <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}\n"
        f"💰 <b>Сумма:</b> {amount:,.2f} сом\n"
        f"📂 <b>Категория:</b> {category}\n"
        f"📝 <b>Цель:</b> {purpose}\n\n"
        f"❓ Сохранить этот расход?"
    )
    
    await message.answer(
        confirmation_text,
        parse_mode="HTML",
        reply_markup=get_confirmation_keyboard()
    )

@router.callback_query(F.data == "confirm_yes", ExpenseForm.waiting_confirmation)
async def confirm_expense(callback: CallbackQuery, state: FSMContext, current_user):
    """Подтверждение и сохранение расхода"""
    try:
        data = await state.get_data()
        amount = data['amount']
        purpose = data['purpose']
        category = data.get('category')
        
        async with AsyncSessionLocal() as db:
            # Сохраняем расход в базу данных
            expense = await ExpenseCRUD.create_expense(
                db=db,
                user_id=current_user.id,
                amount=amount,
                purpose=purpose,
                category_name=category
            )
            
            # Сохраняем в Google Sheets
            await google_sheets_service.add_expense_to_sheet(
                user_name=current_user.full_name,
                amount=amount,
                purpose=purpose,
                expense_date=expense.created_at,
                category=category
            )
            
            # Отмечаем напоминание как выполненное
            today = date.today()
            pending_reminders = await ReminderCRUD.get_pending_reminders(db, today)
            for reminder in pending_reminders:
                if reminder.user_id == current_user.id:
                    await ReminderCRUD.mark_reminder_completed(db, reminder.id)
                    break
        
        success_text = (
            f"✅ <b>Расход успешно сохранен!</b>\n\n"
            f"📊 Данные добавлены в систему учета и Google Таблицу.\n\n"
            f"Что дальше?"
        )
        
        await callback.message.edit_text(
            success_text,
            parse_mode="HTML",
            reply_markup=get_expense_completed_keyboard()
        )
        await callback.answer("Расход сохранен!")
        await state.clear()
        
        logger.info("Expense saved successfully")
        
    except Exception as e:
        logger.error(f"Error saving expense: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при сохранении. Попробуйте позже.")
        await callback.answer()
        await state.clear()

@router.callback_query(F.data == "confirm_no", ExpenseForm.waiting_confirmation)
async def cancel_expense(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления расхода"""
    from bot.keyboards.inline import get_main_menu_keyboard
    
    await callback.message.edit_text(
        "❌ Добавление расхода отменено.\n\n🏠 Возвращаемся в главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer("Отменено")
    await state.clear()