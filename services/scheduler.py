from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from database.database import AsyncSessionLocal
from database.crud import UserCRUD, ReminderCRUD
from services.notifications import NotificationService
from config import config
import pytz
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, bot):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
        self.bot = bot
        self.notification_service = NotificationService(bot)
    
    def start(self):
        """Запуск планировщика"""
        # Ежедневное напоминание в 20:00
        hour, minute = map(int, config.REMINDER_TIME.split(':'))
        
        self.scheduler.add_job(
            self._send_daily_reminders,
            CronTrigger(hour=hour, minute=minute, timezone=pytz.timezone(config.TIMEZONE)),
            id='daily_reminder',
            name='Daily expense reminder'
        )
        
        # Повторные напоминания каждый час после 20:00
        self.scheduler.add_job(
            self._send_hourly_reminders,
            CronTrigger(minute=0, timezone=pytz.timezone(config.TIMEZONE)),
            id='hourly_reminder', 
            name='Hourly reminders'
        )
        
        # Сброс напоминаний в полночь
        self.scheduler.add_job(
            self._reset_daily_reminders,
            CronTrigger(hour=0, minute=0, timezone=pytz.timezone(config.TIMEZONE)),
            id='reset_reminders',
            name='Reset daily reminders'
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    async def _send_daily_reminders(self):
        """Отправка ежедневных напоминаний в 20:00"""
        logger.info("Sending daily reminders")
        
        async with AsyncSessionLocal() as db:
            users = await UserCRUD.get_all_authorized_users(db)
            
            for user in users:
                # Создаем напоминание в БД
                await ReminderCRUD.create_daily_reminder(db, user.id, datetime.now())
                
                # Отправляем уведомление
                await self.notification_service.send_daily_reminder(user.telegram_id)
    
    async def _send_hourly_reminders(self):
        """Отправка почасовых напоминаний для тех, кто не ответил"""
        current_hour = datetime.now(pytz.timezone(config.TIMEZONE)).hour
        
        # Отправляем повторные напоминания только после 20:00 и до 23:59
        if current_hour < 20:
            return
        
        logger.info("Sending hourly reminders")
        
        async with AsyncSessionLocal() as db:
            today = date.today()
            pending_reminders = await ReminderCRUD.get_pending_reminders(db, today)
            
            for reminder in pending_reminders:
                reminder.reminder_count += 1
                await db.commit()
                
                await self.notification_service.send_hourly_reminder(
                    reminder.user.telegram_id, 
                    reminder.reminder_count
                )
    
    async def _reset_daily_reminders(self):
        """Сброс напоминаний в полночь"""
        logger.info("Resetting daily reminders")
        # Здесь можно добавить логику очистки старых напоминаний если нужно
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")