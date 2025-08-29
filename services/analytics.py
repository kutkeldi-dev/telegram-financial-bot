import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from sqlalchemy import func
from database.database import AsyncSessionLocal
from database.models import Expense, User
from typing import List, Dict, Optional
import io
import logging

# Настройка matplotlib для русского текста
rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    async def get_expense_data(self, days: int = 30) -> List[Dict]:
        """Получение данных о расходах за последние N дней"""
        async with AsyncSessionLocal() as db:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # SQLite-совместимый запрос
            from sqlalchemy import text
            result = await db.execute(
                text("""
                SELECT 
                    DATE(expense_date) as date,
                    SUM(amount) as total_amount,
                    COUNT(*) as count,
                    u.full_name as user_name,
                    u.id as user_id
                FROM expenses e
                JOIN users u ON e.user_id = u.id
                WHERE DATE(expense_date) >= :start_date 
                AND DATE(expense_date) <= :end_date
                GROUP BY DATE(expense_date), u.id, u.full_name
                ORDER BY DATE(expense_date)
                """),
                {"start_date": start_date, "end_date": end_date}
            )
            
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def get_user_totals(self, days: int = 30) -> List[Dict]:
        """Получение общих трат по пользователям"""
        async with AsyncSessionLocal() as db:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            from sqlalchemy import text
            result = await db.execute(
                text("""
                SELECT 
                    u.full_name as user_name,
                    SUM(e.amount) as total_amount,
                    COUNT(e.id) as expense_count,
                    AVG(e.amount) as avg_amount
                FROM expenses e
                JOIN users u ON e.user_id = u.id
                WHERE DATE(expense_date) >= :start_date 
                AND DATE(expense_date) <= :end_date
                GROUP BY u.id, u.full_name
                ORDER BY total_amount DESC
                """),
                {"start_date": start_date, "end_date": end_date}
            )
            
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def generate_daily_trend_chart(self, days: int = 30) -> io.BytesIO:
        """Генерация графика трендов по дням"""
        data = await self.get_expense_data(days)
        
        if not data:
            return await self._generate_no_data_chart("Нет данных за указанный период")
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Группируем по дате и суммируем
        daily_totals = df.groupby('date')['total_amount'].sum().reset_index()
        
        # Создаем график
        fig = plt.figure(figsize=(12, 6))
        try:
            plt.plot(daily_totals['date'], daily_totals['total_amount'], 
                    marker='o', linewidth=2, markersize=6, color='#4ECDC4')
            
            plt.title(f'Динамика расходов за последние {days} дней', fontsize=16, pad=20)
            plt.xlabel('Дата', fontsize=12)
            plt.ylabel('Сумма расходов (сом)', fontsize=12)
            
            # Форматирование осей
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
            plt.xticks(rotation=45)
            
            # Добавляем сетку
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Сохраняем в BytesIO
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            return img_buffer
        finally:
            plt.close(fig)  # Always close figure
    
    async def generate_user_pie_chart(self, days: int = 30) -> io.BytesIO:
        """Генерация круговой диаграммы расходов по пользователям"""
        data = await self.get_user_totals(days)
        
        if not data:
            return await self._generate_no_data_chart("Нет данных по пользователям")
        
        # Подготавливаем данные
        users = [item['user_name'] for item in data]
        amounts = [float(item['total_amount']) for item in data]
        
        # Создаем круговую диаграмму
        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(amounts, labels=users, autopct='%1.1f%%', 
                                          colors=self.colors[:len(users)], startangle=90)
        
        plt.title(f'🍰 Распределение расходов по пользователям за {days} дней', 
                 fontsize=16, pad=20)
        
        # Улучшаем читаемость
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.axis('equal')
        
        # Добавляем легенду с суммами
        legend_labels = [f'{user}: {amount:,.0f} сом' 
                        for user, amount in zip(users, amounts)]
        plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
        
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    async def generate_user_comparison_chart(self, days: int = 30) -> io.BytesIO:
        """Генерация столбчатой диаграммы сравнения пользователей"""
        data = await self.get_user_totals(days)
        
        if not data:
            return await self._generate_no_data_chart("Нет данных для сравнения")
        
        # Подготавливаем данные
        users = [item['user_name'] for item in data]
        amounts = [float(item['total_amount']) for item in data]
        counts = [int(item['expense_count']) for item in data]
        
        # Создаем subplot с двумя осями Y
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Столбцы для сумм
        x_pos = np.arange(len(users))
        bars1 = ax1.bar(x_pos - 0.2, amounts, 0.4, label='Сумма расходов', 
                       color='#4ECDC4', alpha=0.8)
        
        ax1.set_xlabel('Пользователи', fontsize=12)
        ax1.set_ylabel('Сумма расходов (сом)', color='#4ECDC4', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='#4ECDC4')
        
        # Вторая ось для количества операций
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x_pos + 0.2, counts, 0.4, label='Количество операций', 
                       color='#FF6B6B', alpha=0.8)
        
        ax2.set_ylabel('Количество операций', color='#FF6B6B', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='#FF6B6B')
        
        # Настройки
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(users, rotation=45, ha='right')
        ax1.set_title(f'📊 Сравнение активности пользователей за {days} дней', 
                     fontsize=16, pad=20)
        
        # Добавляем значения на столбцы
        for bar, amount in zip(bars1, amounts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{amount:,.0f}', ha='center', va='bottom', fontsize=9)
        
        for bar, count in zip(bars2, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{count}', ha='center', va='bottom', fontsize=9)
        
        # Легенда
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    async def generate_weekly_summary_chart(self) -> io.BytesIO:
        """Генерация недельной сводки"""
        data = await self.get_expense_data(7)
        
        if not data:
            return await self._generate_no_data_chart("Нет данных за неделю")
        
        # Группируем по пользователям и дням
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Создаем сводную таблицу
        pivot_table = df.pivot_table(
            index='date', 
            columns='user_name', 
            values='total_amount', 
            fill_value=0,
            aggfunc='sum'
        )
        
        # Создаем stacked bar chart
        plt.figure(figsize=(12, 8))
        
        bottom = np.zeros(len(pivot_table.index))
        
        for i, user in enumerate(pivot_table.columns):
            plt.bar(pivot_table.index, pivot_table[user], 
                   bottom=bottom, label=user, color=self.colors[i % len(self.colors)])
            bottom += pivot_table[user]
        
        plt.title('Недельная сводка расходов по дням и пользователям', 
                 fontsize=16, pad=20)
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Сумма расходов (сом)', fontsize=12)
        
        # Форматирование
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    async def _generate_no_data_chart(self, message: str) -> io.BytesIO:
        """Генерация заглушки при отсутствии данных"""
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, message, ha='center', va='center', 
                fontsize=16, transform=plt.gca().transAxes)
        plt.title('Аналитика расходов', fontsize=18, pad=20)
        plt.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    async def get_analytics_summary(self, days: int = 30) -> str:
        """Получение текстовой сводки аналитики"""
        user_data = await self.get_user_totals(days)
        expense_data = await self.get_expense_data(days)
        
        if not user_data:
            return "📊 Нет данных для анализа"
        
        # Общая сумма
        total_amount = sum(item['total_amount'] for item in user_data)
        total_count = sum(item['expense_count'] for item in user_data)
        avg_per_day = total_amount / days if days > 0 else 0
        
        # Самый активный пользователь
        top_user = max(user_data, key=lambda x: x['total_amount'])
        
        summary = f"""📊 <b>Аналитическая сводка за {days} дней</b>

💰 <b>Общие показатели:</b>
• Всего потрачено: <b>{total_amount:,.2f} сом</b>
• Количество операций: <b>{total_count}</b>
• Средние траты в день: <b>{avg_per_day:.2f} сом</b>

👤 <b>Самый активный:</b>
• {top_user['user_name']} - {top_user['total_amount']:,.2f} сом ({top_user['expense_count']} операций)

📈 <b>Средний чек:</b> {total_amount/total_count if total_count > 0 else 0:.2f} сом"""
        
        return summary
    
    async def get_category_data(self, days: int = 30) -> List[Dict]:
        """Получение данных о расходах по категориям"""
        async with AsyncSessionLocal() as db:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            from sqlalchemy import text
            result = await db.execute(
                text("""
                SELECT 
                    COALESCE(ec.name, 'Без категории') as category_name,
                    SUM(e.amount) as total_amount,
                    COUNT(e.id) as expense_count,
                    AVG(e.amount) as avg_amount
                FROM expenses e
                LEFT JOIN expense_categories ec ON e.category_id = ec.id
                WHERE DATE(expense_date) >= :start_date 
                AND DATE(expense_date) <= :end_date
                GROUP BY ec.name
                ORDER BY total_amount DESC
                """),
                {"start_date": start_date, "end_date": end_date}
            )
            
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def generate_category_pie_chart(self, days: int = 30) -> io.BytesIO:
        """Генерация круговой диаграммы расходов по категориям"""
        data = await self.get_category_data(days)
        
        if not data:
            return await self._generate_no_data_chart("Нет данных по категориям")
        
        # Подготавливаем данные
        categories = [item['category_name'] for item in data]
        amounts = [float(item['total_amount']) for item in data]
        
        # Создаем круговую диаграмму
        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                          colors=self.colors[:len(categories)], startangle=90)
        
        plt.title(f'Расходы по категориям за {days} дней', 
                 fontsize=16, pad=20)
        
        # Улучшаем читаемость
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.axis('equal')
        
        # Добавляем легенду с суммами
        legend_labels = [f'{cat}: {amount:,.0f} сом' 
                        for cat, amount in zip(categories, amounts)]
        plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
        
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer

# Глобальный экземпляр сервиса
analytics_service = AnalyticsService()