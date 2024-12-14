import os
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pathlib import Path
import shutil

# Инициализация Instaloader
L = instaloader.Instaloader()

# Токен вашего Telegram-бота
TELEGRAM_BOT_TOKEN = "7851957608:AAHasR95vqt_Vg7_ZZKQEXq4Nl6D8tq6Wlc"

# ID канала, куда будет отправляться контент
TELEGRAM_CHANNEL_ID = "-1002324153744"



# Функция для скачивания контента из поста Instagram
def download_instagram_post(post_url):
    try:
        # Извлекаем короткое имя поста из URL
        shortcode = post_url.split("/")[-2]
        print(f"Попытка скачать пост с коротким кодом: {shortcode}")  # Логирование

        # Загружаем информацию о посте
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"Информация о посте загружена: {post}")  # Логирование

        # Скачиваем контент
        L.download_post(post, target='instagram_post')
        print(f"Контент скачан: {post.url}")  # Логирование

        # Возвращаем путь к скачанному файлу
        if post.is_video:
            # Очищаем имя файла от недопустимых символов
            file_name = post.video_url.split("/")[-1].split("?")[0]
            print(file_name)
            return f"instagram_post/{file_name}"
        else:
            # Очищаем имя файла от недопустимых символов
            file_name = post.url.split("/")[-1].split("?")[0]
            return f"instagram_post/{file_name}"
    except Exception as e:
        print(f"Ошибка при скачивании контента: {e}")  # Логирование
        return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку на пост Instagram, и я отправлю его контент в канал.")
def find_files_in_directory(directory_path):
    files = []
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith((".jpg", ".mp4")):
            files.append(os.path.join(directory_path, file_name))
    return files

# Функция для очистки директории
def clear_directory(directory_path):
    folder_path = Path(directory_path)
    if not folder_path.exists():
        print(f"Директория {folder_path} не существует.")
        return

    try:
        for item in folder_path.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()  # Удаляем файл или символическую ссылку
                print(f"Удален файл: {item}")
            elif item.is_dir():
                shutil.rmtree(item)  # Удаляем подкаталог
                print(f"Удален подкаталог: {item}")
    except Exception as e:
        print(f"Не удалось очистить директорию {folder_path}: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку на пост Instagram, и я отправлю его контент в канал.")

# Обработчик сообщений с ссылкой на пост Instagram
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текст сообщения
    post_url = update.message.text

    # Проверяем, что это ссылка на пост Instagram
    if "instagram.com/p/" in post_url:
        await update.message.reply_text("Скачиваю контент...")

        # Скачиваем контент
        success = download_instagram_post(post_url)
        if not success:
            await update.message.reply_text("Не удалось скачать контент. Проверьте ссылку.")
            return

        # Ищем все файлы с расширениями .jpg и .mp4 в папке
        files = find_files_in_directory("instagram_post")
        if not files:
            await update.message.reply_text("Контент не найден в папке.")
            return

        # Отправляем каждый файл в канал
        for file_path in files:
            try:
                with open(file_path, "rb") as file:
                    if file_path.endswith(".mp4"):
                        await context.bot.send_video(chat_id=TELEGRAM_CHANNEL_ID, video=file)
                    elif file_path.endswith(".jpg"):
                        await context.bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=file)
            except Exception as e:
                await update.message.reply_text(f"Ошибка при отправке файла {file_path}: {e}")

        await update.message.reply_text("Контент успешно отправлен в канал!")

        # Удаляем все файлы из папки
        clear_directory("instagram_post")
    else:
        await update.message.reply_text("Это не ссылка на пост Instagram.")

# Основная функция
def main():
    # Создаем объект Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()