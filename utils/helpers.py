from datetime import datetime
import re

def format_amount(amount: float) -> str:
    """Форматирование суммы с разделителями тысяч"""
    return f"{amount:,.2f}".replace(",", " ")

def validate_amount(amount_str: str) -> tuple[bool, float]:
    """Валидация и парсинг суммы"""
    try:
        # Заменяем запятую на точку
        amount_str = amount_str.replace(",", ".")
        
        # Удаляем пробелы
        amount_str = re.sub(r'\s', '', amount_str)
        
        # Парсим число
        amount = float(amount_str)
        
        # Проверяем диапазон
        if amount < 0:
            return False, 0.0
        
        if amount > 10000000:  # 10 млн сом максимум
            return False, 0.0
        
        return True, amount
        
    except ValueError:
        return False, 0.0

def format_datetime_kg(dt: datetime) -> str:
    """Форматирование даты и времени для Кыргызстана"""
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    
    day = dt.day
    month = months[dt.month - 1]
    year = dt.year
    time = dt.strftime("%H:%M")
    
    return f"{day} {month} {year} г. в {time}"