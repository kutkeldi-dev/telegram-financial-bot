import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import config
from typing import List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.sheet = None
        self._initialize()
    
    def _initialize(self):
        """Инициализация подключения к Google Sheets"""
        try:
            import os
            import json
            
            # Сначала пробуем переменную окружения (для Railway)
            credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if credentials_json:
                try:
                    credentials_data = json.loads(credentials_json)
                    self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                        credentials_data, self.scope
                    )
                except json.JSONDecodeError:
                    logger.error("Invalid GOOGLE_CREDENTIALS_JSON format")
                    # Fallback на файл
                    self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                        config.GOOGLE_CREDENTIALS, self.scope
                    )
            else:
                # Fallback на файл (для локального запуска)
                self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    config.GOOGLE_CREDENTIALS, self.scope
                )
            self.client = gspread.authorize(self.credentials)
            self.sheet = self.client.open_by_key(config.GOOGLE_SHEETS_ID)
            logger.info("Google Sheets connected successfully")
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets: {e}")
            self.client = None
            self.sheet = None
    
    async def add_expense_to_sheet(self, user_name: str, amount: float, purpose: str, expense_date: datetime, category: str = None):
        """Добавление расхода в таблицу"""
        if not self.client or not self.sheet:
            logger.warning("Google Sheets not connected, skipping expense save")
            return
        try:
            # Получаем или создаем лист "Расходы"
            try:
                worksheet = self.sheet.worksheet("Расходы")
                # Проверяем и обновляем заголовки если нужно
                headers = worksheet.row_values(1)
                if "Категория" not in headers:
                    # Обновляем заголовки для существующего листа
                    worksheet.update("A1:F1", [["Дата", "Пользователь", "Сумма", "Категория", "Цель", "Время записи"]])
            except gspread.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(title="Расходы", rows="1000", cols="7")
                # Добавляем заголовки
                worksheet.append_row(["Дата", "Пользователь", "Сумма", "Категория", "Цель", "Время записи"])
            
            # Добавляем новую строку
            row_data = [
                expense_date.strftime("%d.%m.%Y"),
                user_name,
                float(amount),
                category or "Не указана",
                purpose,
                expense_date.strftime("%d.%m.%Y %H:%M:%S")
            ]
            
            worksheet.append_row(row_data)
            logger.info("Expense added to Google Sheets successfully")
            
        except Exception as e:
            logger.error(f"Error adding expense to Google Sheets: {e}")
    
    async def get_status_data(self) -> Dict[str, any]:
        """Получение данных для статуса из таблицы"""
        if not self.client or not self.sheet:
            logger.warning("Google Sheets not connected, returning empty status")
            return {}
        try:
            # Получаем лист "Статус данные" 
            try:
                worksheet = self.sheet.worksheet("Статус данные")
                # Проверяем и обновляем структуру если нужно
                self._update_status_structure(worksheet)
            except gspread.WorksheetNotFound:
                # Создаем лист если не существует
                worksheet = self.sheet.add_worksheet(title="Статус данные", rows="10", cols="2")
                # Добавляем заголовки и начальные данные
                initial_data = [
                    ["Показатель", "Значение"],
                    ["Общий оборот", "0"],
                    ["Затраты на товар", "0"], 
                    ["Личные затраты", "0"],
                    ["Инвестиции в бизнес", "0"],
                    ["Счет ISKO.TOOLS", "0"],
                    ["Счет TANKER", "0"],
                    ["Остаток в счете", "0"]
                ]
                for row in initial_data:
                    worksheet.append_row(row)
            
            # Получаем все данные
            all_values = worksheet.get_all_values()
            
            # Преобразуем в словарь (пропуская заголовок)
            status_data = {}
            for row in all_values[1:]:  # Пропускаем первую строку (заголовки)
                if len(row) >= 2:
                    key = row[0]
                    value = row[1]
                    try:
                        # Пытаемся преобразовать в число
                        status_data[key] = float(value) if value else 0.0
                    except ValueError:
                        status_data[key] = value
            
            return status_data
            
        except Exception as e:
            logger.error(f"Error getting status data: {e}")
            return {}
    
    def _update_status_structure(self, worksheet):
        """Обновление структуры листа статуса"""
        try:
            # Получаем все данные
            all_values = worksheet.get_all_values()
            if not all_values:
                return
            
            # Проверяем нужно ли обновлять структуру
            existing_keys = [row[0] for row in all_values[1:] if len(row) >= 1]
            
            # Новая структура
            required_keys = [
                "Общий оборот",
                "Затраты на товар", 
                "Личные затраты",
                "Инвестиции в бизнес",
                "Счет ISKO.TOOLS",
                "Счет TANKER",
                "Остаток в счете"
            ]
            
            # Проверяем нужны ли обновления
            updates_needed = []
            
            # Переименование "Долги в рынке" в "Затраты на товар"
            if "Долги в рынке" in existing_keys and "Затраты на товар" not in existing_keys:
                for i, row in enumerate(all_values):
                    if len(row) >= 1 and row[0] == "Долги в рынке":
                        worksheet.update_cell(i+1, 1, "Затраты на товар")
                        break
            
            # Переименование магазинов
            if "Оборот магазин 1" in existing_keys or "Счет магазин 1" in existing_keys:
                for i, row in enumerate(all_values):
                    if len(row) >= 1 and (row[0] == "Оборот магазин 1" or row[0] == "Счет магазин 1"):
                        worksheet.update_cell(i+1, 1, "Счет ISKO.TOOLS")
                        break
                        
            if "Оборот магазин 2" in existing_keys or "Счет магазин 2" in existing_keys:
                for i, row in enumerate(all_values):
                    if len(row) >= 1 and (row[0] == "Оборот магазин 2" or row[0] == "Счет магазин 2"):
                        worksheet.update_cell(i+1, 1, "Счет TANKER")
                        break
            
            # Добавляем отсутствующие поля
            current_data = {row[0]: row[1] if len(row) > 1 else "0" for row in all_values[1:] if len(row) >= 1}
            
            if "Остаток в счете" not in current_data:
                worksheet.append_row(["Остаток в счете", "0"])
                
            logger.info("Status structure updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating status structure: {e}")
    
    async def sync_expenses_from_sheets(self):
        """Синхронизация расходов из Google Sheets в локальную базу"""
        try:
            from database.database import AsyncSessionLocal
            from database.models import Expense, User
            from database.crud import ExpenseCRUD
            from sqlalchemy import select, delete
            from datetime import datetime
            
            # Получаем данные из Google Sheets
            try:
                worksheet = self.sheet.worksheet("Расходы")
                all_values = worksheet.get_all_values()
            except gspread.WorksheetNotFound:
                logger.info("No expenses sheet found in Google Sheets")
                return
            
            if len(all_values) <= 1:  # Только заголовок или пусто
                # Google Sheets пустая - очищаем локальную базу
                async with AsyncSessionLocal() as db:
                    # Удаляем все расходы
                    await db.execute(delete(Expense))
                    await db.commit()
                    logger.info("Local expenses cleared - Google Sheets is empty")
                return
            
            # Получаем данные из Google Sheets (пропускаем заголовок)
            sheet_expenses = []
            for row in all_values[1:]:
                if len(row) >= 6:
                    try:
                        category_value = row[3] if len(row) > 3 and row[3] and row[3].strip() != "Не указана" else None
                        
                        expense_data = {
                            'date': datetime.strptime(row[0], "%d.%m.%Y").date(),
                            'user_name': row[1],
                            'amount': float(row[2]),
                            'category': category_value,
                            'purpose': row[4],
                            'created_at': datetime.strptime(row[5], "%d.%m.%Y %H:%M:%S")
                        }
                        
                        sheet_expenses.append(expense_data)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Skipping invalid row in Google Sheets: {row}, error: {e}")
                        continue
            
            # Синхронизируем с локальной базой
            async with AsyncSessionLocal() as db:
                # Получаем всех пользователей
                users_result = await db.execute(select(User))
                users = {user.full_name: user for user in users_result.scalars().all()}
                
                # Очищаем существующие расходы
                await db.execute(delete(Expense))
                
                # Добавляем расходы из Google Sheets
                for expense_data in sheet_expenses:
                    user = users.get(expense_data['user_name'])
                    if user:
                        # Create expense with proper parameters
                        from database.models import Expense, ExpenseCategory
                        from sqlalchemy import select
                        
                        # Get or create category
                        category_id = None
                        if expense_data['category']:
                            result = await db.execute(select(ExpenseCategory).where(ExpenseCategory.name == expense_data['category']))
                            category = result.scalar_one_or_none()
                            if not category:
                                category = ExpenseCategory(name=expense_data['category'])
                                db.add(category)
                                await db.flush()
                            category_id = category.id
                        
                        # Create expense
                        expense = Expense(
                            user_id=user.id,
                            amount=expense_data['amount'],
                            purpose=expense_data['purpose'],
                            category_id=category_id,
                            expense_date=expense_data['created_at'],
                            created_at=expense_data['created_at']
                        )
                        db.add(expense)
                
                # КРИТИЧЕСКИ ВАЖНО: Коммитим изменения!
                await db.commit()
                logger.info(f"Synced {len(sheet_expenses)} expenses from Google Sheets to local database")
                
        except Exception as e:
            logger.error(f"Error syncing expenses from Google Sheets: {e}")

# Глобальный экземпляр сервиса
google_sheets_service = GoogleSheetsService()