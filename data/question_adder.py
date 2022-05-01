from questions import Question


def add_question(question_text, complexity, film, first_answer_variant,
                   second_answer_variant, third_answer_variant, right_answer):
    global db_session
    session = db_session.create_session()

    question = Question()

    if film == pirates_of_the_caribbean:
        question.film_id = 1
    elif film == peaky_blinders:
        question.film_id = 2
    elif film == home_alone:
        question.film_id = 3
    elif film == diamond_hand:
        question.film_id = 4
    elif film == the_gentlemen:
        question.film_id = 5

    question.question = question_text
    question.complexity = complexity

    answer_variants = ';'.join([first_answer_variant, second_answer_variant, third_answer_variant])

    question.answer_variants = answer_variants
    question.right_answer = right_answer

    session.add(question)
    session.commit()
