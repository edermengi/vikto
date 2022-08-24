import logging
import re
from random import Random

from common.model import AskQuestion
from common.service import broadcast
from common.storage import db, fact_sheet, util
from common.storage.db import QuizEntity, FactSheetEntity, GameState, QuizType
from common.storage.db_util import Add
from common.storage.str_util import replace_random_letters

log = logging.getLogger(__name__)

WAIT_SECONDS = 300


class SelectOneComposer:
    NUMBER_OF_OPTIONS = 4

    def __init__(self, quiz: QuizEntity, sheet: FactSheetEntity):
        self.quiz = quiz
        self.sheet = sheet
        self.wait_seconds = WAIT_SECONDS

    @staticmethod
    def _pick_answer_and_questions(sheet_rows, answer_column, question_column):
        sheet_rows = [row for row in sheet_rows if (row[answer_column] and row[question_column])]
        log.info(f'Found {len(sheet_rows)} rows to select from')
        answer_row = Random().choice(sheet_rows)
        answer_options = {answer_row[answer_column]: answer_row}
        while len(answer_options) != SelectOneComposer.NUMBER_OF_OPTIONS and len(answer_options) != len(sheet_rows):
            question_row = Random().choice(sheet_rows)
            answer_option = question_row[answer_column]
            if answer_option not in answer_options:
                answer_options[answer_option] = question_row

        return answer_row, [v for v in answer_options.values()]

    def compose_question(self):
        sheet_rows = fact_sheet.load_rows(self.sheet.fileKey)
        log.info(f'Loaded sheet {self.sheet.fileKey} of {len(sheet_rows)} rows')
        answer_row, all_rows = self._pick_answer_and_questions(sheet_rows, self.quiz.answerColumn,
                                                               self.quiz.questionColumn)
        log.info(f'Randomly picked answer {answer_row} and options {all_rows}')
        Random().shuffle(all_rows)
        question = {
            'quizType': self.quiz.quizType,
            'question': self.quiz.question,
            'questionItem': answer_row[self.quiz.questionColumn],
            'questionItemType': self.sheet.column_type(self.quiz.questionColumn),
            'questionHintItem': answer_row[self.quiz.questionHintColumn] if self.quiz.questionHintColumn else None,
            'questionHintItemType': self.sheet.column_type(
                self.quiz.questionHintColumn) if self.quiz.questionHintColumn else None,
            'title': self.quiz.title,
            'answer': answer_row[self.quiz.answerColumn],
            'answerType': self.sheet.column_type(self.quiz.answerColumn),
            'answerHint': answer_row[self.quiz.answerHintColumn] if self.quiz.answerHintColumn else None,
            'answerHintType': self.sheet.column_type(
                self.quiz.answerHintColumn) if self.quiz.answerHintColumn else None,
            'answerOptions': [{
                'answer': row[self.quiz.answerColumn],
                'hint': row[self.quiz.answerHintColumn] if self.quiz.answerHintColumn else None
            }
                for row in all_rows
            ]
        }
        return question


class TypeOneComposer:

    def __init__(self, quiz: QuizEntity, sheet: FactSheetEntity):
        self.quiz = quiz
        self.sheet = sheet
        self.wait_seconds = WAIT_SECONDS

    def compose_question(self):
        sheet_rows = fact_sheet.load_sample_rows(self.sheet.fileKey, list(self.sheet.columns))
        log.info(f'Loaded sheet {self.sheet.fileKey} of {len(sheet_rows)} sample rows')
        row = Random().choice(sheet_rows)
        answer = row[self.quiz.answerColumn]
        answer_hint = replace_random_letters(answer, '.', 0.70)
        question = {
            'quizType': self.quiz.quizType,
            'question': self.quiz.question,
            'questionItem': row[self.quiz.questionColumn],
            'questionItemType': self.sheet.column_type(self.quiz.questionColumn),
            'title': self.quiz.title,
            'answer': answer,
            'answerHint': answer_hint
        }
        return question


class TypeOneFromSetComposer:

    def __init__(self, quiz: QuizEntity, sheet: FactSheetEntity):
        self.quiz = quiz
        self.sheet = sheet
        self.wait_seconds = WAIT_SECONDS

    def compose_question(self):
        sheet_rows = fact_sheet.load_sample_rows(self.sheet.fileKey, list(self.sheet.columns))
        log.info(f'Loaded sheet {self.sheet.fileKey} of {len(sheet_rows)} sample rows')
        row = Random().choice(sheet_rows)

        variants = row[self.quiz.answerColumn]
        variants = variants.upper()

        all_options = [variant.strip() for variant in re.split('[,;]', variants) if variant]
        question_item = Random().choice(all_options) if self.quiz.answerColumn == self.quiz.questionColumn else row[
            self.quiz.questionColumn]
        answers = [option for option in all_options if option != question_item]

        question = {
            'quizType': self.quiz.quizType,
            'question': self.quiz.question,
            'questionItem': question_item,
            'questionItemType': self.sheet.column_type(self.quiz.questionColumn),
            'title': self.quiz.title,
            'answer': ",".join(answers),
        }
        return question


def ask_question(payload: AskQuestion):
    game_id = payload.gameId

    game = db.get_game(game_id)
    quizzes = db.get_quizzes(game.topic.topic if game.topic else 'RU')
    log.info(f'Found {len(quizzes)} quizzes')
    quiz: QuizEntity = Random().choice(quizzes)
    log.info(f'Randomly choose quiz {quiz}')
    sheet: FactSheetEntity = db.get_fact_sheet(quiz.factSheet)
    log.info(f'Retrieved fact sheet {sheet}')

    if quiz.quizType == QuizType.SELECT_ONE:
        composer = SelectOneComposer(quiz, sheet)
    elif quiz.quizType == QuizType.TYPE_ONE:
        composer = TypeOneComposer(quiz, sheet)
    elif quiz.quizType == QuizType.TYPE_ONE_FROM_SET:
        composer = TypeOneFromSetComposer(quiz, sheet)
    else:
        raise ValueError(f'Unsupported quiz type {quiz.quizType}')

    question = composer.compose_question()

    log.info(f'Saving question: {question}')
    db.update_game(game_id,
                   question=question,
                   gameState=GameState.ASK_QUESTION,
                   taskToken=payload.taskToken,
                   questionNo=Add(1),
                   timerStart=util.now_timestamp(),
                   timerSeconds=composer.wait_seconds)
    broadcast.send_game_state(game_id)
