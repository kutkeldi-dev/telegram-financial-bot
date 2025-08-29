from aiogram.fsm.state import StatesGroup, State

class ExpenseForm(StatesGroup):
    waiting_amount = State()
    waiting_category = State()
    waiting_purpose = State()
    waiting_confirmation = State()