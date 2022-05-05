from data import db_session
from data.films import Film
from data.questions import Question
from data.question_adder import add_question


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
