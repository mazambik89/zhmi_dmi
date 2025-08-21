# Telegram Guide Bot (aiogram 3)

## 🚀 Возможности
- Выдаёт PDF-гайд за подписку на канал
- Проверяет подписку перед отправкой
- Логирует пользователей (ID, username, дата, получил ли PDF)
- Команда /stats (для админа)
- Антифлуд (нельзя получить гайд чаще 1 раза в час)
- Красивые кнопки и приветствие

## 📂 Установка
1. Склонировать проект или распаковать архив
2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Переименовать `.env.example` → `.env` и заполнить:
   ```env
   BOT_TOKEN=ваш_токен
   ADMIN_ID=ваш_telegram_id
   CHANNEL_ID=-100id_канала
   ```
4. Положить PDF в `files/guide.pdf`
5. Запустить:
   ```bash
   python main.py
   ```

## 🌐 Деплой на Render
- Создать новый Web Service
- Загрузить проект
- В `Start Command` указать:
  ```bash
  python main.py
  ```
- Добавить переменные окружения (BOT_TOKEN, ADMIN_ID, CHANNEL_ID)
