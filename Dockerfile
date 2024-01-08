# Используйте официальный образ Python
FROM python:3.10.11

# Устанавливаем зависимости
RUN pip install aiogram==2.25.1

# Создаем директорию для приложения
RUN mkdir -p /Pepper_bot

# Копируем файлы приложения в контейнер
COPY Bot_cleaner_pepper_url.py /Pepper_bot/
COPY run.sh /Pepper_bot/

# Устанавливаем рабочую директорию
WORKDIR /Pepper_bot

# Даем права на выполнение скрипта
RUN chmod +x run.sh

# Команда для запуска скрипта
CMD ["./run.sh"]
