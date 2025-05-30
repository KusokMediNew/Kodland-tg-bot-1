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
    bot.send_message(message.chat.id, "👋 Привет! Я твой простой Telegram-бот.\n\nДоступные команды:\n/start – Перезапустить бота\n/search <текст> или /search – найти текст в Google\n\nПросто напиши мне любой текст, и я помогу найти его в Google! 🔎".replace('<', '&lt;').replace('>', '&gt;'))

# Обработчик команды /search с текстом
@bot.message_handler(commands=['search'])
def search_handler(message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        search_text = args[1].strip()
        # Проверка на плохие слова
        search_text_no_spaces = search_text.replace(' ', '')
        found_bad = []
        for bad_word in BAD_WORDS:
            if bad_word in search_text_no_spaces or re.search(rf"\b{bad_word}\b", search_text):
                found_bad.append(bad_word)
        if found_bad:
            bot.send_message(message.chat.id, f"Это плохой запрос ❌\nПлохие слова: {', '.join(found_bad)}")
            return
        keyboard = telebot.types.InlineKeyboardMarkup()
        search_button = telebot.types.InlineKeyboardButton(
            text="🔎 Искать в Google",
            url=f"https://www.google.com/search?q={search_text.replace(' ', '+')}"
        )
        keyboard.add(search_button)
        bot.send_message(
            message.chat.id,
            f'Ты написал: <b>"{search_text}"</b>\n\n👇 Найти это в Google:',
            reply_markup=keyboard
        )
    else:
        msg = bot.send_message(
            message.chat.id,
            "🔎 <b>Что найти?</b>\n\n"
            "1️⃣ Введите поисковый запрос ниже, и я помогу найти его в Google!\n"
            "2️⃣ Не используйте непристойные слова — такие запросы не обрабатываются.\n\n"
            "✍️ Жду ваш запрос!"
        )
        bot.register_next_step_handler(msg, process_search_text)

def process_search_text(message):
    search_text = message.text.strip()
    search_text_no_spaces = search_text.replace(' ', '')
    found_bad = []
    for bad_word in BAD_WORDS:
        if bad_word in search_text_no_spaces or re.search(rf"\b{bad_word}\b", search_text):
            found_bad.append(bad_word)
    if found_bad:
        bot.send_message(message.chat.id, f"Это плохой запрос ❌\nПлохие слова: {', '.join(found_bad)}")
        return
    keyboard = telebot.types.InlineKeyboardMarkup()
    search_button = telebot.types.InlineKeyboardButton(
        text="🔎 Искать в Google",
        url=f"https://www.google.com/search?q={search_text.replace(' ', '+')}"
    )
    keyboard.add(search_button)
    bot.send_message(
        message.chat.id,
        f'Ты написал: <b>"{search_text}"</b>\n\n👇 Найти это в Google:',
        reply_markup=keyboard
    )

# Обработчик всех остальных текстовых сообщений (не команд)
@bot.message_handler(func=lambda message: message.content_type == 'text' and not message.text.startswith('/'))
def ignore_text(message):
    bot.send_message(message.chat.id, "Я реагирую только на команды. Используйте /search для поиска.")

# Точка входа: запуск бота
if __name__ == "__main__":
    if LOGGING:
        logging.info("Бот запущен...")
    bot.polling(none_stop=True)
