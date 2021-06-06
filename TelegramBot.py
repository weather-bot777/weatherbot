import json
import requests
import logging
import datetime
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlighter import SQLighter
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем соединение с БД
db = SQLighter('db.db')

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("Ссылка на погоду")
button2 = KeyboardButton("Ссылка на статистику")
button3 = KeyboardButton("subscribe")
button4 = KeyboardButton("unsubscribe")
markup1 = ReplyKeyboardMarkup().row(
    button3, button4).add(button1).add(button2)


@dp.message_handler(commands="start")
""" Команда для начала взаимодействия с ботом."""
async def process_command(message: types.Message):
    """ Функция, отправляющая пользователю приветственное сообщение с интрукцией по использованию бота
    
        Параметры: 
            message (Message) : сообщение  
    """
    await message.reply("Привет! Я бот-Weather/COVID.\n"
                        "________________________________\n"
                        "---Напиши /weather и город на русском или английском через пробел, чтобы получить погоду. \n"
                        "Например: ''/weather Moscow''\n"
                         "________________________________\n"
                        "---Напиши /covid и название страны на английском, чтобы получить статистику заболеваемости и смертности от COVID-19.\n"
                        "Например: ''/covid Russia''\n"
                         "________________________________\n"
                        "---Выбери одну из кнопок ниже, чтобы подписаться/отписаться на/от расслыки или получить ссылки на источники погоды/статистики.", reply_markup=markup1)

@dp.message_handler(commands="weather")
""" Команда для получения прогноза погоды. """
async def cmd_weather(message: types.Message):
    """ Функция, принимающая сообщение пользователя с городом. Обращается по API к сайту openweathermap, возвращает пользователю погоду в заданном городе
    
        Параметры: 
            message (Message) : сообщение пользователя
    """
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text.split()[1]}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = round((data["main"]["pressure"]) * 0.750062, 1)
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])
        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                            f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                            f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                            f"***Хорошего дня!***"
                            )
        return
    except:
        await message.reply("\U00002620 Проверьте название города \U00002620")


@dp.message_handler(commands="covid")
""" Команда для получения статистики заболеваемости и смертности от COVID-19."""
async def cmd_covid(message: types.Message):
 """ Функция, принимающая сообщение пользователя с городом или страной. Обращается по API к сайту https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/stats, возвращает пользователю статистику по заданному городу/стране
    
        Параметры: 
            message (Message) : сообщение пользователя
    """

    url = "https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/stats"

    c = message.text.split()[1]

    querystring = {"country": c}

    headers = {
        'x-rapidapi-host': "covid-19-coronavirus-statistics.p.rapidapi.com",
        'x-rapidapi-key': "2c1e350ee9msh4e6242c72e6458bp1e3ad2jsn39ac77e7abe7"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        json_data = json.loads(response.text)
        country = str(json_data['data']['covid19Stats'][0]['country'])
        lastUpdate = str(json_data['data']['covid19Stats'][0]['lastUpdate'])
        deaths = str(json_data['data']['covid19Stats'][0]['deaths'])
        confirmed = str(json_data['data']['covid19Stats'][0]['confirmed'])
        recovered = str(json_data['data']['covid19Stats'][0]['recovered'])
        await message.reply(
            'Страна: ' + country + '\nДата: ' + lastUpdate + '\nВыявлено: ' + confirmed + '\nВыздоровело: ' + recovered + '\nУмерло: ' + deaths)
    except:
        await message.reply("Не понял")


@dp.message_handler(Text(equals="Ссылка на погоду"))
""" Хэндлер, сравнивающий сообщение пользователя с текстом ССЫЛКА НА ПОГОДУ. При совпадении выполняет команду."""
async def with_puree(message: types.Message):
""" Функция, выполняющаяся в случае совпадения текста. Возвращает пользователю ссылку на источник погоды
    
    Параметры: 
        message (Message) : сообщение пользователя
"""
    await message.reply("https://www.gismeteo.ru/weather-moscow-4368/")


@dp.message_handler(Text(equals="Ссылка на статистику"))
""" Хэндлер, сравнивающий сообщение пользователя с текстом ССЫЛКА НА СТАТИСТИКУ. При совпадении выполняет команду."""
async def with_puree(message: types.Message):
""" Функция, выполняющаяся в случае совпадения текста. Возвращает пользователю ссылку на источник статистики
    
    Параметры: 
        message (Message) : сообщение пользователя
"""
    await message.reply("https://yandex.ru/covid19/stat")


# Команда активации подписки
@dp.message_handler(Text(equals="subscribe"))
""" Хэндлер, сравнивающий сообщение пользователя с текстом subscribe. При совпадении выполняет функцию with_puree."""
async def with_puree(message: types.Message):
""" Функция, добавляющая пользователя в БД в случае его отсутствия или просто обновляющая его статус подписки. Возвращает пользователю сообщение об успешной активации подписки.
    
    Параметры: 
        message (Message) : сообщение пользователя
"""    
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Вы успешно подписались на рассылку!")


# Команда отписки
@dp.message_handler(Text(equals="unsubscribe"))
""" Хэндлер, сравнивающий сообщение пользователя с текстом subscribe. При совпадении выполняет функцию with_puree."""
async def with_puree(message: types.Message):
""" Функция, добавляющая пользователя в БД в случае его отсутствия или просто обновляющая его статус подписки. Возвращает пользователю сообщение об успешной отписке.
    
    Параметры: 
        message (Message) : сообщение пользователя
"""  
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
