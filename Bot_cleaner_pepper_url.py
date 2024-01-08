#Bot_cleaner_pepper_url - это бот для конвертации ссылки pepper, которую получаем из "поделиться" в приложении.
#https://github.com/Pushkin31/Bot_cleaner_pepper_url

import re
import json
import atexit
import types
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram import executor

TOKEN = 'YOUR_TOKEN'  # Заменить 'YOUR_TOKEN' на токен бота
TARGET_USER_ID = 123456789  # ID Пользователя, от кого считаем кол-во ссылок

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def remove_path_from_url(url):
    cleaned_url = url.replace('/share-deal-from-app', '')
    return cleaned_url

# Паттерн для поиска ссылок вида https://www.pepper.ru/share-deal-from-app/*
url_pattern = re.compile(r'https://www\.pepper\.ru/share-deal-from-app/\d+')

# Счетчик для конкретного пользователя
user_counter = 0

# Загрузка счетчика из файла
try:
    with open('counter.json', 'w') as f:
        json.dump(user_counter, f)
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")

def save_counter():
    # Сохранение счетчика в файл
    with open('counter.json', 'w') as f:
        json.dump(user_counter, f)

atexit.register(save_counter)

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

# Обработка счетчика только для указанного ID
    if message.from_user.id == TARGET_USER_ID:
        global user_counter
        user_counter += 1
        await message.reply(f"{cleaned_url}\n\nЭто уже {user_counter} неправильная ссылка с 29.12.2023", parse_mode=types.ParseMode.MARKDOWN)
    else:
        await message.reply(cleaned_url, parse_mode=types.ParseMode.MARKDOWN)

    # Удаляем исходное сообщение пользователя
    await bot.delete_message(message.chat.id, message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)