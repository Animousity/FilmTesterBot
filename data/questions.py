import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    question_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    film = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    complexity = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answer_variants = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    right_answer = sqlalchemy.Column(sqlalchemy.String, nullable=False)
