import telegram

from data import db_session
import random
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


# Запускаем logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5106957189:AAFCPjSNNQWtuLtmYp62v9kdmU5hoZQnaRk'

responsive_keyboard_for_movie_selection = [['Пираты Карибского моря'], ['Острые козырьки'], ['Один Дома'], ['Бриллиантовая рука'], ['Джентльмены']]

markup = ReplyKeyboardMarkup(responsive_keyboard_for_movie_selection, one_time_keyboard=True)

question = ''
selected_film = ''
selected_difficulty_level = ''
get_message_bot = ''
points_scored = 0
question_list = []
right_answer = ''


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def start(update, context):
    first_name = update.message.from_user.first_name
    update.message.reply_text(
        f"Добро пожаловать, {first_name}!\nЯ - FilmTesterBot - бот, при помощи которого вы можете проходить тесты на знание фильмов.\nВыберите фильм, чтобы начать.\nЧтобы узнать больше, вы можете прописать команду /help.",
        reply_markup=markup
    )
    return 1


def stop(update, context):
    first_name = update.message.from_user.first_name
    update.message.reply_text(
        f"До встречи, {first_name}!\nНадеюсь, вам понравилось проходить тесты!")
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(
        "Чтобы начать заново, пропишите команду /start.\nЧтобы завершить сеанс, пропишите команду /stop.\n")


def request_questions():
    global selected_film
    global selected_difficulty_level

    questions_list = []

    for q in session.query(Question).filter(Question.film == selected_film,
                                            Question.complexity == selected_difficulty_level):
        answers = q.answer_variants.split(';')
        answers = set(answers)
        answers = list(answers)
        questions_list.append([q.question, answers, q.right_answer])

    return questions_list


def first_response(update, context):
    global selected_film
    global selected_difficulty_level

    selected_film = update.message.text
    response_keyboard_to_select_difficulty = [['Легкий'], ['Средний'], ['Трудный']]
    markup_for_level_selection = ReplyKeyboardMarkup(response_keyboard_to_select_difficulty, one_time_keyboard=True)
    update.message.reply_text(
        f"Отличный выбор!\nТеперь выберите уровень сложности, чтобы продолжить!", reply_markup=markup_for_level_selection)

    return 2


def second_response(update, context):
    global selected_difficulty_level
    global selected_film

    selected_difficulty_level = update.message.text

    film = session.query(Film).filter(Film.name == selected_film)
    response_keyboard_to_questions_continue = [['Перейти к вопросам']]
    markup_for_questions_continue = ReplyKeyboardMarkup(response_keyboard_to_questions_continue, one_time_keyboard=True)

    update.message.reply_text(
        f"Фильм: {selected_film}\nСложность: {selected_difficulty_level}", reply_markup=markup_for_questions_continue)

    return 3


def first_question(update, context):
    global question_list
    global right_answer
    global points_scored

    question_list = request_questions()
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клавиатуре
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 4


def second_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клавиатуре
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)
    
    if answer == right_answer:
        points_scored += 1
    
    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 5


def third_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клавиатуре
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 6


def fourth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это вывод вопроса
    # это кнопочки на клавиатуре
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 7


def fifth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 8


def sixth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это вывод вопроса
    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 9


def seventh_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 10


def eighth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 11


def ninth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]
    return 12


def tenth_question(update, context):
    global question_list
    global right_answer
    global points_scored

    answer = update.message.text
    question_number = random.randint(0, len(question_list) - 1)

    # это кнопочки на клаве
    response_keyboard_to_select_question = [[question_list[question_number][1][0]],
                                            [question_list[question_number][1][1]],
                                            [question_list[question_number][1][2]]]

    markup_for_question = ReplyKeyboardMarkup(response_keyboard_to_select_question, one_time_keyboard=True)

    update.message.reply_text(
        f"{question_list[question_number][0]}", reply_markup=markup_for_question)

    if answer == right_answer:
        points_scored += 1

    # это правильный ответ
    right_answer = question_list[question_number][2]

    del question_list[question_number]

    context.user_data.clear()
    return 13


def ending(update, context):
    global right_answer
    global points_scored

    answer = update.message.text

    points_word = ''

    if answer == right_answer:
        points_scored += 1

    if points_scored == 0 or points_scored >= 5:
        points_word = 'баллов'
    elif points_scored == 1:
        points_word = 'балл'
    elif 2 <= points_scored <= 4:
        points_word = 'балла'

    if points_scored <= 3:
        update.message.reply_text(
            f"Вы набрали {points_scored} {points_word}. Мы советуем освежить знания по этому фильму. Чтобы начать заново, нажмите /start")
    elif 4 <= points_scored <= 6:
        update.message.reply_text(
            f"Вы набрали {points_scored} {points_word}. Достаточно неплохо, но ещё нельзя назвать вас знатоком этого фильма. Чтобы начать заново, нажмите /start")
    elif 7 <= points_scored <= 9:
        update.message.reply_text(
            f"Вы набрали {points_scored} {points_word}. Поздравляем, вы очень хорошо знаете этот фильм! Чтобы начать заново, нажмите /start")
    elif points_scored == 10:
        update.message.reply_text(
            f"Вы набрали {points_scored} {points_word}. Поздравляем, вы ответили правильно на все 10 вопросов. Вы - настоящий знаток! Чтобы начать заново, нажмите /start")

    return ConversationHandler.END


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text & ~Filters.command, first_response, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text & ~Filters.command, second_response, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            3: [MessageHandler(Filters.text & ~Filters.command, first_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            4: [MessageHandler(Filters.text & ~Filters.command, second_question, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            5: [MessageHandler(Filters.text & ~Filters.command, third_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            6: [MessageHandler(Filters.text & ~Filters.command, fourth_question, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            7: [MessageHandler(Filters.text & ~Filters.command, fifth_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            8: [MessageHandler(Filters.text & ~Filters.command, sixth_question, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            9: [MessageHandler(Filters.text & ~Filters.command, seventh_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            10: [MessageHandler(Filters.text & ~Filters.command, eighth_question, pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            11: [MessageHandler(Filters.text & ~Filters.command, ninth_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            12: [MessageHandler(Filters.text & ~Filters.command, tenth_question, pass_user_data=True)],
            # Функция читает ответ на первый вопрос и задаёт второй.
            13: [MessageHandler(Filters.text & ~Filters.command, ending, pass_user_data=True)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Создаём обработчик сообщений типа Filters.text
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # Регистрируем обработчик в диспетчере.

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(conv_handler)

    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
