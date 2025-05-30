import telebot
import logging
import re
from config import TOKEN, ADMINS, LOGGING

# Настройка логирования: если LOGGING=True, выводим подробные логи, иначе только критические ошибки
if LOGGING:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.CRITICAL)  # Отключить обычные логи

# Инициализация бота с поддержкой HTML-разметки
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Список запрещённых слов (русский мат и английские непристойные слова)
BAD_WORDS = [
    # Русский мат (30 слов/фраз)
    "хуй", "пизда", "ебать", "ебаный", "ебан", "ебло", "еблан", "ебарь", "ебля", "ебучий", "ёб", "ёбаный",
    "мудак", "мудила", "манда", "мандовошка", "мандавошка", "гандон", "залупа", "пидор", "пидорас", "пидрила",
    "пидрилла", "пидорка", "пидорок", "пидорюга", "пидорюжка", "пидорчонок", "пидорчиха", "пидорюга", "пидорюжка",
    # Английские непристойные слова (30+)
    "pornhub", "sex", "xxx", "porn", "anal", "oral", "gay", "lesbian", "erotic", "fuck", "shit", "bitch", "cunt",
    "pussy", "dick", "cock", "penis", "vagina", "masturbate", "masturbation", "cum", "sperm", "orgasm", "blowjob",
    "handjob", "fisting", "incest", "rape", "bestiality", "zoophilia", "childporn", "child porn", "child sex",
    "pedophile", "slut", "whore", "asshole", "jerkoff", "wank", "spank", "suck", "deepthroat", "rimjob", "felch",
    "twat", "motherfucker", "nigger", "fag", "faggot", "tranny", "cumshot", "gangbang", "milf", "bdsm", "bondage"
]

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    if LOGGING:
        logging.info(f"Пользователь {message.from_user.id} запустил бота.")
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я твой простой Telegram-бот.\n\n"
        "Доступные команды:\n"
        "/start – Перезапустить бота\n\n"
        "Просто напиши мне любой текст, и я помогу найти его в Google! 🔎"
    )

# Главный обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def unknown_message(message):
    if LOGGING:
        logging.info(f"Пользователь {message.from_user.id} отправил неизвестное сообщение: {message.text}")
    search_text = message.text.lower()
    # Удаляем все пробелы для поиска плохих слов с пробелами
    search_text_no_spaces = search_text.replace(' ', '')
    found_bad = []
    for bad_word in BAD_WORDS:
        # Проверяем наличие запрещённых слов как слитно, так и с пробелами
        if bad_word in search_text_no_spaces or re.search(rf"\\b{bad_word}\\b", search_text):
            found_bad.append(bad_word)
    if found_bad:
        # Если найдено запрещённое слово — отправляем предупреждение и список слов
        bot.send_message(message.chat.id, f"Это плохой запрос ❌\nПлохие слова: {', '.join(found_bad)}")
        return
    # Если всё хорошо — предлагаем поискать в Google
    keyboard = telebot.types.InlineKeyboardMarkup()
    search_button = telebot.types.InlineKeyboardButton(
        text="🔎 Искать в Google",
        url=f"https://www.google.com/search?q={search_text.replace(' ', '+')}"
    )
    keyboard.add(search_button)
    bot.send_message(
        message.chat.id,
        f'Ты написал: <b>"{message.text}"</b>\n\n👇 Найти это в Google:',
        reply_markup=keyboard
    )

# Точка входа: запуск бота
if __name__ == "__main__":
    if LOGGING:
        logging.info("Бот запущен...")
    bot.polling(none_stop=True)
