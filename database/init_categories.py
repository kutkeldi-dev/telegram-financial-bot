from database.database import AsyncSessionLocal
from database.models import ExpenseCategory
from sqlalchemy import select
import asyncio

async def init_expense_categories():
    """Initialize default expense categories"""
    categories = [
        "Личные затраты",
        "Жылдызбек ава", 
        "Инвестиция",
        "Услуга",
        "Другое"
    ]
    
    async with AsyncSessionLocal() as db:
        # Check if categories already exist
        result = await db.execute(select(ExpenseCategory))
        existing_categories = result.scalars().all()
        
        if existing_categories:
            print("Categories already exist, skipping initialization")
            return
        
        # Create categories
        for category_name in categories:
            category = ExpenseCategory(name=category_name)
            db.add(category)
        
        await db.commit()
        print(f"Created {len(categories)} expense categories")

if __name__ == "__main__":
    asyncio.run(init_expense_categories())