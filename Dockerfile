# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем папку для скачивания контента
RUN mkdir -p /app/instagram_post

# Открываем порт для Telegram-бота (если нужно)
EXPOSE 80

# Команда для запуска бота
CMD ["python", "bot.py"]