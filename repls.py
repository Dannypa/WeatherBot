from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

finished_register = ("Отлично, язык установлен.", "Great, the language is set.")
send_loc = (
    "Отправьте ваше местоположение (город и страну) "
    "или нажмите на большую кнопку и отправьте свою геопозицию",
    "Send the location (city and country) or press the big button and send your location")
send_loc_no_geo = (
    "Отправьте ваше местоположение (город и страну)",
    "Send the location (city and country)")
forecast = ("Прогноз на завтра", "Forecast for tomorrow")
current_weather = ("Погода сейчас", "Current weather")
what_now = ("Что бы вы хотели узнать?", "What would you like to know?")
location_unavailable = ("Похоже, такое место недоступно. Попробуйте ещё раз!",
                        "Seems like this location is unavailable. Choose another one, please!")
current_weather_text = ("Температура: {}°C.\n{}.\nВлажность {}%.\nСкорость ветра - {} км/ч.\nОщущается на {}°C.",
                        "Temperature is {}°C.\nThe weather is {}.\nHumidity is {}%.\nWind is {} kph."
                        "\nIn total, fells like {}.")
forecast_text = ("Температура {}°C.\n{}.\nВлажность {}%.", "Temperature is {}°C.\nThe weather is {}.\nHumidity is {}%.")
sample_text = ("Жду указаний.", "Waiting for your call.")
loc_kb = [ReplyKeyboardMarkup(one_time_keyboard=True), ReplyKeyboardMarkup(one_time_keyboard=True)]
loc_kb[0].add(KeyboardButton("Отправить геопозицию", request_location=True))
loc_kb[1].add(KeyboardButton("Send location", request_location=True))
