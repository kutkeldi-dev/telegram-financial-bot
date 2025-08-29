# Развертывание бота на Railway

Этот документ содержит пошаговые инструкции по развертыванию Telegram финансового бота на платформе Railway.

## Шаг 1: Подготовка GitHub репозитория

✅ **Уже выполнено** - репозиторий создан по адресу:
https://github.com/kutkeldi-dev/telegram-financial-bot

## Шаг 2: Создание проекта на Railway

1. **Регистрация/Вход:**
   - Перейдите на https://railway.app
   - Войдите через GitHub аккаунт

2. **Создание нового проекта:**
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Найдите и выберите репозиторий `kutkeldi-dev/telegram-financial-bot`

3. **Настройка переменных окружения:**
   
   В разделе **Variables** добавьте следующие переменные:

   **Обязательные переменные:**
   ```
   BOT_TOKEN=8311452814:AAEV5MN3oVK88YFAhrMFTTCs0TCUFtuW7Z8
   GOOGLE_SHEETS_ID=1LOnq99hRyoK4CMj2YfaNO5EVrR74CzdmXoSFgvO5mXQ
   AUTH_CODE_USER1=isko2025
   AUTH_CODE_USER2=kutujp
   AUTH_CODE_USER3=12345
   ```

   **GOOGLE_CREDENTIALS_JSON** - скопируйте всю строку из файла `credentials_env.txt`

   **Опциональные переменные:**
   ```
   TIMEZONE=Asia/Bishkek
   REMINDER_TIME=20:00
   DEBUG=False
   ```

## Шаг 3: Добавление PostgreSQL базы данных

1. **В проекте Railway:**
   - Нажмите "New" → "Database" → "Add PostgreSQL"
   - База данных создастся автоматически
   - Railway автоматически создаст переменную `DATABASE_URL`

## Шаг 4: Развертывание

1. **Railway автоматически начнет развертывание**
2. **Следите за логами в разделе "Deployments"**
3. **Если все настроено правильно - бот запустится автоматически**

## Шаг 5: Проверка работы

1. **Проверьте логи развертывания** - не должно быть ошибок
2. **Протестируйте бота в Telegram:**
   - Найдите @fin_wb_tracker_bot
   - Отправьте `/start`
   - Введите код авторизации: `isko2025` или `kutujp`
   - Попробуйте добавить расход
   - Проверьте статус и аналитику

## Важные моменты

### Безопасность
- ✅ Все секретные данные исключены из git
- ✅ Используются переменные окружения
- ✅ Google credentials передаются как JSON строка

### Автоматическое масштабирование
- ✅ Railway автоматически перезапускает бота при сбоях
- ✅ Настроены retry политики в railway.toml

### База данных
- ✅ Автоматическое переключение с SQLite на PostgreSQL
- ✅ Поддержка миграций

## Устранение неполадок

### Ошибка: "message can't be edited"
**Исправлено** - обновлен обработчик аналитики для текстовых сообщений.

### Ошибка: "Conflict: terminated by other getUpdates request"
**Решение:** Остановите локальную версию бота - только один экземпляр может работать с одним токеном.

### Проблема: "Google credentials not found"
**Решение:** Проверьте переменную `GOOGLE_CREDENTIALS_JSON` - она должна быть валидным JSON в одну строку.

### Проблема: "Database connection failed"  
**Решение:** Убедитесь что PostgreSQL база данных создана в Railway.

## Полезные ссылки

- Railway Dashboard: https://railway.app/dashboard
- GitHub Repository: https://github.com/kutkeldi-dev/telegram-financial-bot
- Telegram Bot: @fin_wb_tracker_bot