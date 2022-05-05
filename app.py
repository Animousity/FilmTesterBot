from data import db_session
from data.films import Film
from data.questions import Question
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext
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


def add_question(question_text, complexity, film, first_answer_variant,
                 second_answer_variant, third_answer_variant, right_answer):

    question = Question()

    question.film = film

    question.question = question_text
    question.complexity = complexity

    answer_variants = ';'.join([first_answer_variant, second_answer_variant, third_answer_variant])

    question.answer_variants = answer_variants
    question.right_answer = right_answer

    session.add(question)
    session.commit()


with open('data/questions.txt', mode='r') as file:
    file_lines = file.readlines()
    movie = ''
    hardness = ''

    for line in file_lines:

        if line == 'Пираты Карибского моря\n':
            movie = 'Пираты Карибского моря'

        elif line == 'Острые козырьки\n':
            movie = 'Острые козырьки'

        elif line == 'Один Дома\n':
            movie = 'Один Дома'

        elif line == 'Бриллиантовая рука\n':
            movie = 'Бриллиантовая рука'

        elif line == 'Джентльмены\n':
            movie = 'Джентльмены'

        elif line == 'Легкий\n':
            hardness = 'Легкий'

        elif line == 'Средний\n':
            hardness = 'Средний'

        elif line == 'Трудный\n':
            hardness = 'Трудный'

        if ';' in line:
            line_elements = line.split(';')
            answers = line_elements[2].replace('(', '').replace(')', '').replace('\n', '').split(',')

            add_question(question_text=line_elements[1], complexity=hardness, film=movie,
                         first_answer_variant=answers[0], second_answer_variant=answers[1],
                         third_answer_variant=answers[2], right_answer=answers[0])


# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5106957189:AAFCPjSNNQWtuLtmYp62v9kdmU5hoZQnaRk'

responsive_keyboard_for_movie_selection = [['Пираты Карибского моря'], ['Острые козырьки'], ['Один дома'], ['Бриллиантовая рука'], ['Джентльмены']]

markup = ReplyKeyboardMarkup(responsive_keyboard_for_movie_selection, one_time_keyboard=True)

question = ''
select_film = ''
selected_difficulty_level = ''
get_message_bot = ''
points_scored = 0



def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )




def start(update, context):
    username = update.message.from_user.username
    update.message.reply_text(
        f"Добро пожаловать, {username}!\nЯ - TestFilmBot - бот, при помощи которого вы можете проходить тесты на знание фильмов.\nВыберите фильм, чтобы начать.",
    reply_markup=markup
    )
    return 1

def stop(update, context):
    username = update.message.from_user.username
    update.message.reply_text(
        f"До встречи, {username}!\nНадеюсь, вам понравилось проходить тесты!")


def help(update, context):
    update.message.reply_text(
        "что")


def first_response(update, context):
    global select_film
    global selected_difficulty_level

    select_film = update.message.text
    response_keyboard_to_select_difficulty = [['Легкий'], ['Средний'], ['Трудный']]
    markup_for_level_selection = ReplyKeyboardMarkup(response_keyboard_to_select_difficulty, one_time_keyboard=True)

    update.message.reply_text(
        f"Отличный выбор!\nТеперь выберите уровень сложности, чтобы продолжить!", reply_markup=markup_for_level_selection)
    return 2


def second_response(update, context):
    global selected_difficulty_level

    selected_difficulty_level = update.message.text
    update.message.reply_text(
        f"Хорошо. Итак, первый вопрос:\n{question}{selected_difficulty_level}")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    # Точка входа в диалог.
    # В данном случае — команда /start. Она задаёт первый вопрос.
    entry_points=[CommandHandler('start', start)],

    # Состояние внутри диалога.
    # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
    states={
        # Функция читает ответ на первый вопрос и задаёт второй.
        1: [MessageHandler(Filters.text & ~Filters.command, first_response)],
        # Функция читает ответ на второй вопрос и завершает диалог.
        2: [MessageHandler(Filters.text & ~Filters.command, second_response)]
    },

    # Точка прерывания диалога. В данном случае — команда /stop.
    fallbacks=[CommandHandler('stop', stop)]
)


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
    dp.add_handler(CommandHandler("stop", stop))

    #dp.add_handler(MessageHandler(Filters.text, level_selection))
    #dp.add_handler(MessageHandler(Filters.text, answers_on_questions))

    dp.add_handler(MessageHandler(Filters.text, first_response))
    dp.add_handler(MessageHandler(Filters.text, second_response))

    dp.add_handler(conv_handler)



    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
