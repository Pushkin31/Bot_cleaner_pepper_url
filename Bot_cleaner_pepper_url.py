# Bot_cleaner_pepper_url - это бот для конвертации ссылки pepper, которую получаем из "поделиться" в приложении.
# https://github.com/Pushkin31/Bot_cleaner_pepper_url

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
                        "https://www.pepper.ru/share-deal-from-app/*", reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply("Этот бот помогает Аркаше решить проблему с отправкой ссылок из приложения Pepper и конвертировать их в ссылку, которая откроется у любого человека, даже если нет установленного приложения")

@dp.message_handler(lambda message: message.text == "О боте")
async def about_bot(message: types.Message):
    await help_command(message)



@dp.message_handler(lambda message: message.text and url_pattern.search(message.text))
async def process_url(message: types.Message):
    original_url = message.text
    cleaned_url = remove_path_from_url(original_url)

    # Обработка счетчика
    user_id = message.from_user.id

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

    # Вывод сообщения с учетом счетчика
    await message.reply(
        f"{cleaned_url}\n\nЭто уже {count} неправильная ссылка с 29.12.2023",
        parse_mode=types.ParseMode.MARKDOWN)

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(message.chat.id, message.message_id)


# Закрываем подключение к базе данных при завершении программы
def on_exit():
    conn.close()


atexit.register(on_exit)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
