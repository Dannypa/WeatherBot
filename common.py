from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

welcome_text = "Привет! Я - простой бот, чтобы узнать погоду сейчас или прогноз погоды.\n" \
               "Для этого используйте команду /weather.\n" \
               "<>\n" \
               "Hello! I am a simple bot to get weather forecast or current weather.\n" \
               "To get weather forecast or find out current weather in your location, use the /weather command."
unfinished_registration = "Пожалуйста, выберите язык\n" \
                          "<>\n" \
                          "Please, set language"

lang_kb = InlineKeyboardMarkup()
lang_kb.add(InlineKeyboardButton("Русский", callback_data="ru"))
lang_kb.add(InlineKeyboardButton("English", callback_data="en"))
