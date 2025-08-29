from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import User, Expense, DailyReminder, ExpenseCategory
from datetime import datetime, date
from typing import Optional, List

class UserCRUD:
    @staticmethod
    async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, telegram_id: int, username: str, full_name: str, auth_code: str) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            auth_code=auth_code,
            is_authorized=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_all_authorized_users(db: AsyncSession) -> List[User]:
        result = await db.execute(select(User).where(User.is_authorized == True))
        return result.scalars().all()

class ExpenseCRUD:
    @staticmethod
    async def create_expense(db: AsyncSession, user_id: int, amount: float, purpose: str, category_name: Optional[str] = None) -> Expense:
        category_id = None
        if category_name:
            # Найти или создать категорию
            result = await db.execute(select(ExpenseCategory).where(ExpenseCategory.name == category_name))
            category = result.scalar_one_or_none()
            if not category:
                category = ExpenseCategory(name=category_name)
                db.add(category)
                await db.flush()
            category_id = category.id
        
        expense = Expense(
            user_id=user_id,
            amount=amount,
            purpose=purpose,
            category_id=category_id
        )
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return expense
    
    @staticmethod
    async def get_user_expenses_by_date(db: AsyncSession, user_id: int, target_date: date) -> List[Expense]:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        result = await db.execute(
            select(Expense)
            .where(and_(
                Expense.user_id == user_id,
                Expense.expense_date >= start_datetime,
                Expense.expense_date <= end_datetime
            ))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_expenses_by_date(db: AsyncSession, target_date: date) -> List[Expense]:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        result = await db.execute(
            select(Expense)
            .options(selectinload(Expense.user))
            .where(and_(
                Expense.expense_date >= start_datetime,
                Expense.expense_date <= end_datetime
            ))
        )
        return result.scalars().all()

class ReminderCRUD:
    @staticmethod
    async def create_daily_reminder(db: AsyncSession, user_id: int, reminder_date: datetime) -> DailyReminder:
        reminder = DailyReminder(
            user_id=user_id,
            reminder_date=reminder_date
        )
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        return reminder
    
    @staticmethod
    async def get_pending_reminders(db: AsyncSession, target_date: date) -> List[DailyReminder]:
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        result = await db.execute(
            select(DailyReminder)
            .options(selectinload(DailyReminder.user))
            .where(and_(
                DailyReminder.reminder_date >= start_datetime,
                DailyReminder.reminder_date <= end_datetime,
                DailyReminder.is_completed == False
            ))
        )
        return result.scalars().all()
    
    @staticmethod
    async def mark_reminder_completed(db: AsyncSession, reminder_id: int):
        result = await db.execute(select(DailyReminder).where(DailyReminder.id == reminder_id))
        reminder = result.scalar_one_or_none()
        if reminder:
            reminder.is_completed = True
            await db.commit()