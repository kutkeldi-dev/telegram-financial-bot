from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline import get_main_menu_keyboard, get_main_reply_keyboard

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 <b>Добро пожаловать в Финансового Бота!</b>\n\n"
        "🔐 Для начала работы вам необходимо авторизоваться.\n"
        "Используйте команду: <code>/auth ВАШ_КОД</code>\n\n"
        "📞 За получением кода обратитесь к администратору."
    )
    
    await message.answer(welcome_text, parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """Возврат в главное меню"""
    menu_text = (
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        menu_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

# Обработчики текстовых команд (кнопки клавиатуры)
@router.message(F.text == "📊 Статус")
async def status_text_handler(message: Message, current_user):
    """Обработчик текстовой команды Статус"""
    from bot.handlers.status import show_status_data
    await show_status_data(message, current_user)

@router.message(F.text == "💰 Расход")
async def expense_text_handler(message: Message, current_user, state: FSMContext):
    """Обработчик текстовой команды Расход"""
    from bot.handlers.expenses import start_expense_input
    
    class FakeCallbackQuery:
        def __init__(self, message):
            self.message = message
            self.data = "expense"
        async def answer(self):
            pass
    
    fake_callback = FakeCallbackQuery(message)
    await start_expense_input(fake_callback, state, current_user)

@router.message(F.text == "📈 Аналитика")
async def analytics_text_handler(message: Message, current_user):
    """Обработчик текстовой команды Аналитика"""
    from bot.keyboards.inline import get_analytics_keyboard
    from services.analytics import analytics_service
    
    keyboard = get_analytics_keyboard()
    summary = await analytics_service.get_analytics_summary()
    text = f"{summary}\n\n🎯 Выберите тип аналитики:"
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.message(F.text == "📖 Помощь")
async def help_text_handler(message: Message, current_user):
    """Обработчик текстовой команды Помощь"""
    help_text = (
        f"👤 <b>{current_user.full_name}</b>\n"
        f"📖 <b>Помощь по использованию бота</b>\n\n"
        
        f"🔹 <b>📊 Статус</b> - показать финансовый статус\n"
        f"🔹 <b>💰 Расход</b> - добавить новый расход\n"
        f"🔹 <b>📈 Аналитика</b> - графики и отчеты\n"
        
        f"💡 <b>Команды:</b>\n"
        f"• <code>/start</code> - начать работу\n"
        f"• <code>/auth КОД</code> - авторизация\n"
        f"• <code>/analytics</code> - аналитика\n"
        f"• <code>/sync</code> - синхронизация\n\n"
        
        f"❓ По вопросам обращайтесь к администратору."
    )
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())

@router.message()
async def show_main_menu(message: Message, current_user):
    """Показ главного меню для авторизованных пользователей"""
    menu_text = (
        f"👤 <b>{current_user.full_name}</b>\n"
        f"🏠 <b>Главное меню</b>\n\n"
        "Используйте кнопки внизу экрана для быстрого доступа к функциям:"
    )
    
    await message.answer(
        menu_text,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard()
    )