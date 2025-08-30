# Как запускать бота

## 🚀 Локальный запуск

### Подготовка
```bash
# 1. Очистить pending updates (если нужно)
python -c "import requests; from config import config; requests.post(f'https://api.telegram.org/bot{config.BOT_TOKEN}/deleteWebhook', json={'drop_pending_updates': True})"

# 2. Запустить бота
python main.py
```

## ☁️ Railway (облачная версия)

### Как остановить Railway версию:
1. Зайти на https://railway.app/dashboard  
2. Найти проект `telegram-financial-bot`
3. Остановить развертывание

### Как запустить Railway версию:
1. Остановить локальную версию (Ctrl+C)
2. На Railway нажать "Deploy"

## ⚠️ ВАЖНО: Конфликт версий

**Только одна версия может работать одновременно!**

❌ **НЕ запускайте локальную и Railway версии одновременно** - это создает конфликт pending updates.

### Если появляется конфликт:
```bash
# Очистить pending updates
python -c "import requests; from config import config; requests.post(f'https://api.telegram.org/bot{config.BOT_TOKEN}/deleteWebhook', json={'drop_pending_updates': True})"
```

## 🔧 Тестирование

После запуска любой версии проверьте:

1. **Команда `/start`** - должен ответить приветствием
2. **Авторизация `/auth isko2025`** - для пользователя "Ислам"  
3. **Авторизация `/auth kutujp`** - для пользователя "Куткелди"

## 📊 Функции бота

- 📊 **Статус** - финансовые данные из Google Sheets
- 💰 **Расходы** - добавление новых трат
- 📈 **Аналитика** - графики и отчеты
- ⏰ **Напоминания** - ежедневно в 20:00
- 🔄 **Синхронизация** - автоматическая каждый час

## 🐛 Решение проблем

### "Bot is not responding"
- Остановите Railway версию
- Очистите pending updates  
- Запустите локально

### "Conflict: terminated by other getUpdates"
- Две версии работают одновременно
- Остановите одну из них