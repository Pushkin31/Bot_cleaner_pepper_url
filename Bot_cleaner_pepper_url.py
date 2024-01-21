import re
import sqlite3
import atexit
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram import executor

# Заменить 'YOUR_TOKEN' на токен бота
TOKEN = 'YOUR_TOKEN'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Создаем подключение к базе данных SQLite
conn = sqlite3.connect('counters.db')
cursor = conn.cursor()

# Создаем таблицу, если она еще не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS counters (
        user_id INTEGER PRIMARY KEY,
        count INTEGER
    )
''')
conn.commit()


def remove_path_from_url(url):
    cleaned_url = url.replace('/share-deal-from-app', '')
    return cleaned_url

# Паттерн для поиска ссылок вида https://www.pepper.ru/share-deal-from-app/*
url_pattern = re.compile(r'https://www\.pepper\.ru/share-deal-from-app/\d+')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("О боте"))

    await message.reply("Привет! Этот бот реагирует только на сообщения, содержащие ссылки вида "
                        '"https://www.pepper.ru/share-deal-from-app/*"', reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply("Этот бот помогает решить проблему с отправкой ссылок из приложения Pepper и конвертировать их в ссылку, которая откроется у любого человека, даже если нет установленного приложения.")


@dp.message_handler(lambda message: message.text == "О боте")
async def about_bot(message: types.Message):
    await help_command(message)


@dp.message_handler(lambda message: message.text and url_pattern.search(message.text))
async def process_url(message: types.Message):
    original_url = message.text
    cleaned_url = remove_path_from_url(original_url)

    # Получаем информацию о пользователе, отправившем сообщение
    user = message.from_user
    user_id = user.id
    user_username = user.username
    user_first_name = user.first_name
    user_last_name = user.last_name

    # Получаем информацию о пользователе, на чье сообщение был данный ответ
    replied_user = message.reply_to_message.from_user if message.reply_to_message else None

    # Извлекаем информацию о пользователе, если она доступна
    if replied_user:
        try:
            f"[{replied_user.first_name} {replied_user.last_name}](tg://user?id={replied_user.id})"
        except AttributeError:
            f"[{replied_user.first_name or ''} {replied_user.last_name or ''}](tg://user?id={replied_user.id})"

    # Получаем текущее значение счетчика из базы данных
    cursor.execute('SELECT count FROM counters WHERE user_id=?', (user_id,))
    result = cursor.fetchone()

    if result:
        count = result[0]
    else:
        count = 0

    # Увеличиваем значение счетчика на единицу
    count += 1

    # Сохраняем или обновляем значение счетчика в базе данных
    cursor.execute('INSERT OR REPLACE INTO counters (user_id, count) VALUES (?, ?)', (user_id, count))
    conn.commit()

    # Формируем упоминание пользователя
    if user_username:
        user_mention = f"[{user_username}](tg://user?id={user_id})"
    else:
        user_mention = f"[{user_first_name or ''} {user_last_name or ''}](tg://user?id={user_id})"

    # Вывод сообщения с учетом счетчика и упоминания пользователя
    reply_text = f"{cleaned_url}\n\n{user_mention}, это уже {count} неправильная ссылка с 29.12.2023"

    # Отправляем ответное сообщение
    await message.reply(reply_text, parse_mode=types.ParseMode.MARKDOWN)

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(message.chat.id, message.message_id)


# Закрываем подключение к базе данных при завершении программы
def on_exit():
    conn.close()


atexit.register(on_exit)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
