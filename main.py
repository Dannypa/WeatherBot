import logging
import aiogram
import config
from aiogram import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json
import re
import repls
import common
import os
import decs

logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="a+")
bot = aiogram.Bot(config.TOKEN)
dp = aiogram.Dispatcher(bot)

state = dict()  # 1 for forecast waiting, 2 for current, 0 for nothing, -1 for unfinished registration
lang = dict()


@decs.handle_exception
def load_data():
    if os.stat("data.json").st_size == 0:
        return
    with open("data.json") as f:
        old_data = json.load(f)
    for uid in old_data:
        state[int(uid)], lang[int(uid)] = old_data[uid]


@decs.handle_exception
def save_data():
    to_save = {}
    for uid in state:
        if uid in lang:
            to_save[uid] = (state[uid], lang[uid])
    with open("data.json", 'w') as f:
        json.dump(to_save, f)


@decs.a_handle_exception
async def send_help(uid, username=""):
    if uid not in state:
        state[uid] = -1
        logging.info(f"New user! {uid = }, {username = }")
    await bot.send_message(uid, common.welcome_text, reply_markup=common.lang_kb)


@decs.a_handle_exception
@dp.message_handler(commands=['help', 'start'])
async def handle_help(message: aiogram.types.Message):
    await send_help(message.chat.id, message.from_user.username)


@decs.a_handle_exception
@dp.message_handler(commands=['weather'])
async def send_weather(message: aiogram.types.Message):
    user_id = message.chat.id
    if user_id not in state:
        await send_help(message.chat.id)
        return
    if state[user_id] == -1:
        await bot.send_message(user_id, common.unfinished_registration)
        return
    kb = InlineKeyboardMarkup()
    l = lang[user_id]
    kb.add(InlineKeyboardButton(repls.forecast[l], callback_data="forecast"))
    kb.add(InlineKeyboardButton(repls.current_weather[l], callback_data="current"))
    await bot.send_message(message.chat.id, repls.what_now[l], reply_markup=kb)


@decs.handle_exception
def get_request_text(q: str, is_forecast: bool, l: int):
    text = f"https://api.weatherapi.com/v1/" \
           f"{'forecast' if is_forecast else 'current'}.json?key={config.WEATHER_API_KEY}" \
           f"&q={q}{'&days=2' if is_forecast else ''}&aqi=no&lang={('ru', 'en')[l]}"
    return text


@decs.a_handle_exception
async def get_resp(user_id, text):
    l = lang[user_id]
    pat = "[+-]?([0-9]*[.])?[0-9]+"
    q = text
    if not re.match(f"{pat},{pat}", text.replace(' ', '')):
        r = requests.get(
            f"https://api.tomtom.com/search/2/geocode/{text}.json"
            f"?storeResult=false&view=Unified&key={config.PLACE_API_KEY}"
        )
        data = json.loads(r.text)["results"]
        if len(data) == 0:
            return -1
        pos = data[0]["position"]
        lat, lon = pos["lat"], pos["lon"]
        q = f"{lat},{lon}"
    resp = requests.get(get_request_text(q, (state[user_id] != 2), l))
    return resp


@decs.a_handle_exception
async def get_data(user_id, text):
    data = await get_resp(user_id, text)
    l = lang[user_id]
    if data == -1:
        await bot.send_message(user_id, repls.location_unavailable[l])
        return {}
    data = json.loads(data.text)
    if "error" in data:
        await bot.send_message(user_id, repls.location_unavailable[l])
        return {}
    return data


@decs.a_handle_exception
async def handle_request(user_id, m_text):
    if user_id not in state:
        await send_help(user_id)
        return
    if state[user_id] == -1:
        await bot.send_message(user_id, common.unfinished_registration)
        return
    l = lang[user_id]
    if state[user_id] == 0:
        await bot.send_message(user_id, repls.use_weather[l])
        return
    data = await get_data(user_id, m_text)
    if len(data) == 0:
        return
    if state[user_id] == 2:
        data = data['current']
    elif state[user_id] == 1:
        data = data["forecast"]["forecastday"][1]["hour"][11]
    text = repls.current_weather_text[l].format(data['temp_c'], data['condition']['text'],
                                                data['humidity'], data['wind_kph'],
                                                data['feelslike_c'])
    await bot.send_message(user_id, text)
    state[user_id] = 0


@decs.a_handle_exception
@dp.message_handler(content_types=['text'])
async def text_handler(message: aiogram.types.Message):
    uid = message.chat.id
    if uid == config.ADMIN_ID and message.text == config.SHUTDOWN_TEXT:
        save_data()
        await bot.send_message(uid, "Data is saved.")
    await handle_request(uid, message.text)


@decs.a_handle_exception
@dp.message_handler(content_types=['location'])
async def handle_location(message: aiogram.types.Message):
    user_id = message.chat.id
    if (user_id not in state) or state[user_id] == 0:
        await send_weather(message)
        return
    lat = message.location.latitude
    lon = message.location.longitude
    await handle_request(user_id, f"{lat},{lon}")


@decs.a_handle_exception
@dp.callback_query_handler(lambda c: c.data in {"forecast", "current"})
async def forecast(c: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(c.id)
    user_id = c.message.chat.id
    state[user_id] = 1 if c.data == "forecast" else 2
    cl = lang[user_id]
    if c.message.reply_markup is not None:
        await bot.edit_message_reply_markup(user_id, c.message.message_id, None)
    if c.message.chat.type == aiogram.types.ChatType.PRIVATE:
        await bot.send_message(user_id, repls.send_loc[cl], reply_markup=repls.loc_kb[cl])
    else:
        await bot.send_message(user_id, repls.send_loc_no_geo[cl])


@decs.a_handle_exception
@dp.callback_query_handler(lambda c: c.data in {"ru", "en"})
async def forecast(c: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(c.id)
    user_id = c.message.chat.id
    if c.data == "ru":
        lang[user_id] = 0
    else:
        lang[user_id] = 1
    state[user_id] = 0
    await bot.edit_message_reply_markup(user_id, c.message.message_id, None)
    await bot.send_message(user_id, repls.finished_register[lang[user_id]])


def main():
    load_data()
    executor.start_polling(dp, timeout=600)


if __name__ == '__main__':
    main()
