import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import Filters


# Установка уровня логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализация токена бота и экземпляра класса Updater
TOKEN = '2093573180:AAF66iwNcU5UgI9Sz7YUIwTN1y3l0yX-uEg'
updater = Updater(token=TOKEN, use_context=True)

# Обработчик команды /start
def start(update, context):
    user_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton("Да", callback_data='yes'),
                 InlineKeyboardButton("Нет", callback_data='no')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Будешь сегодня на парах?', reply_markup=reply_markup)

# Обработчик коллбек-кнопок
def button_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    answer = query.data

    # Сохранение ответа пользователя
    context.user_data[user_id] = answer

    # Ответ пользователю
    query.answer()

    # Следующий вопрос
    if answer == 'no':
        query.edit_message_text('Какая причина пропуска пары?')
    else:
        query.edit_message_text('Отлично! Буду ждать тебя на парах!')

# Обработчик сообщений с причиной пропуска пары
def skip_reason(update, context):
    user_id = update.effective_user.id
    skip_reason = update.message.text

    # Сохранение причины пропуска пары
    context.user_data[user_id] = skip_reason

    update.message.reply_text('Хорошо, причина сохранена!')

# Функция, которая отправляет сообщение администратору
def admin(update, context):
    # Пароль, который должен вводить администратор для получения списка пользователей
    password = '227'

    # ID чата с администратором
    admin_chat_id = "1107708377"

    # Проверка пароля
    if context.args and context.args[0] == password:
        # Получение списка пользователей, которые не будут на парах
        user_answers = context.user_data
        users_not_coming = []
        for user, answer in user_answers.items():
            if answer == 'no':
                users_not_coming.append(str(user))

        # Сброс списка ответов пользователей
        user_answers.clear()

        # Отправка сообщения админу со списком пользователей, которые не будут на парах
        if users_not_coming:
            message = f"Сегодня не будут на парах: {', '.join(users_not_coming)}"
        else:
            message = "Сегодня все будут на парах!"

        context.bot.send_message(chat_id=admin_chat_id, text=message)

        update.message.reply_text('Список пользователей отправлен админу')
    else:
        update.message.reply_text('Неверный пароль!')

# Обработчик неизвестных команд
def unknown_command(update, context):
    update.message.reply_text("Извините, я не понимаю эту команду.")

# Функция main() для запуска бота
def main():
    # Создание диспетчера и добавление обработчиков
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))

    # Обработчик коллбек-кнопок
    dp.add_handler(CallbackQueryHandler(button_callback))

    # Обработчик причин пропуска пары
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, skip_reason))

    # Обработчик неизвестных команд
    dp.add_handler(MessageHandler(Filters.command, unknown_command))

    # Запуск бота
    updater.start_polling()

    # Остановка бота при нажатии Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()

