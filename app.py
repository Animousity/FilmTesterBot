from data import db_session
from data.films import Film
from data.questions import Question
from data.question_adder import add_question
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
from telegram import ReplyKeyboardRemove


db_session.global_init("db/films.db")

pirates_of_the_caribbean = Film()
pirates_of_the_caribbean.name = "Пираты Карибского моря"
pirates_of_the_caribbean.picture = "pictures/pirates_of_the_caribbean.jpg"

peaky_blinders = Film()
peaky_blinders.name = "Острые козырьки"
peaky_blinders.picture = "pictures/peaky_blinders.jpeg"

home_alone = Film()
home_alone.name = "Один дома"
home_alone.picture = "pictures/home_alone.jpg"

diamond_hand = Film()
diamond_hand.name = "Бриллиантовая рука"
diamond_hand.picture = "pictures/diamond_hand.jpeg"

the_gentlemen = Film()
the_gentlemen.name = "Джентльмены"
the_gentlemen.picture = "pictures/the_gentlemen.jpg"

session = db_session.create_session()

session.query(Film).delete()
session.query(Question).delete()

session.add(pirates_of_the_caribbean)
session.add(peaky_blinders)
session.add(home_alone)
session.add(diamond_hand)
session.add(the_gentlemen)

session.commit()

with open('questions.txt', mode='r') as file:
    file_lines = file.readlines()
    film = ''
    complexity = ''
    i = 0

    for line in file_lines:

        if line == 'Пираты Карибского моря':
            film = pirates_of_the_caribbean
        elif line == 'Острые козырьки':
            film = peaky_blinders
        elif line == 'Один Дома':
            film = home_alone
        elif line == 'Бриллиантовая рука':
            film = diamond_hand
        elif line == 'Джентльмены':
            film = the_gentlemen

        if line == 'Лёгкий':
            complexity = 'Лёгкий'
        elif line == 'Средний':
            complexity = 'Средний'
        elif line == 'Трудный':
            complexity = 'Трудный'

        line_elements = line.split(';')
        answers = line_elements[2].replace('(', '').replace(')', '').split(',')

        add_question(line_elements[1], complexity, film,
                     answers[0], answers[1], answers[2], answers[0])


# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5106957189:AAFCPjSNNQWtuLtmYp62v9kdmU5hoZQnaRk'

reply_keyboard = [['Пираты Карибского моря'], ['Острые козырьки'], ['Один дома'], ['Бриллиантовая рука'], ['Джентльмены']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)



def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )

# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
def start(update, context):
    username = update.message.from_user.username
    update.message.reply_text(
        f"Добро пожаловать, {username}!\nЯ - TestFilmBot - бот, при помощи которого вы можете проходить тесты на знание фильмов.\nВыберите фильм и уровень сложности, чтобы начать.",
    reply_markup=markup
    )


def stop(update, context):
    username = update.message.from_user.username
    update.message.reply_text(
        f"До встречи, {username}!\nНадеюсь, вам понравилось проходить тесты!")

def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")

def pirates_of_the_Caribbean(update, context):
    update.message.reply_text(
        "asd")

def peaky_Blinders(update, context):
    update.message.reply_text(
        "bebra")


def home_Alone(update, context):
    update.message.reply_text(
        "")


def the_diamond_arm(update, context):
    update.message.reply_text("")


def the_Gentlemen(update, context):
    update.message.reply_text(
        "")




# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    #keyboard




    # Создаём обработчик сообщений типа Filters.text
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))

    dp.add_handler(MessageHandler(Filters.text, pirates_of_the_Caribbean))
    dp.add_handler(MessageHandler(Filters.text, peaky_Blinders))
   # dp.add_handler(MessageHandler("home_Alone", home_Alone))
   # dp.add_handler(MessageHandler("the_diamond_arm", the_diamond_arm))
   # dp.add_handler(MessageHandler("the_Gentlemen", the_Gentlemen))

    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()