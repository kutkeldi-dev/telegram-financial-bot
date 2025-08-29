from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Расход", callback_data="expense")],
        [InlineKeyboardButton(text="📊 Статус", callback_data="status")],
        [InlineKeyboardButton(text="📈 Аналитика", callback_data="analytics")],
        [InlineKeyboardButton(text="📖 Инструкция", callback_data="instructions")],
    ])
    return keyboard

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с командами внизу экрана"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статус"), KeyboardButton(text="💰 Расход")],
            [KeyboardButton(text="📈 Аналитика"), KeyboardButton(text="📖 Помощь")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        persistent=True
    )
    return keyboard

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no")
        ]
    ])
    return keyboard

def get_expense_completed_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после добавления расхода"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
        [InlineKeyboardButton(text="💰 Добавить еще расход", callback_data="expense")]
    ])
    return keyboard

def get_category_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории расходов"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ Личные затраты", callback_data="category_1")],
        [InlineKeyboardButton(text="2️⃣ Жылдызбек ава", callback_data="category_2")],
        [InlineKeyboardButton(text="3️⃣ Инвестиция", callback_data="category_3")],
        [InlineKeyboardButton(text="4️⃣ Услуга", callback_data="category_4")],
        [InlineKeyboardButton(text="5️⃣ Другое", callback_data="category_5")],
    ])
    return keyboard

def get_analytics_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для аналитики"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Тренд (7 дней)", callback_data="chart_trend_7"),
            InlineKeyboardButton(text="📈 Тренд (30 дней)", callback_data="chart_trend_30")
        ],
        [
            InlineKeyboardButton(text="🍰 Круговая (7 дней)", callback_data="chart_pie_7"),
            InlineKeyboardButton(text="🍰 Круговая (30 дней)", callback_data="chart_pie_30")
        ],
        [
            InlineKeyboardButton(text="📊 Сравнение (7 дней)", callback_data="chart_comparison_7"),
            InlineKeyboardButton(text="📊 Сравнение (30 дней)", callback_data="chart_comparison_30")
        ],
        [
            InlineKeyboardButton(text="📅 Недельная сводка", callback_data="chart_weekly")
        ],
        [
            InlineKeyboardButton(text="📊 Категории (7 дней)", callback_data="chart_category_7"),
            InlineKeyboardButton(text="📊 Категории (30 дней)", callback_data="chart_category_30")
        ],
        [
            InlineKeyboardButton(text="📋 Отчет (7 дней)", callback_data="summary_7"),
            InlineKeyboardButton(text="📋 Отчет (30 дней)", callback_data="summary_30")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])
    return keyboard