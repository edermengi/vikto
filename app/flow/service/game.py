import logging
from random import Random

from common.model import WaitPlayersReady, AskQuestion, ShowAnswer
from common.storage import db, fact_sheet
from common.storage.db import QuizEntity, FactSheetEntity, PlayerEntity, GameState
from common.service import broadcast

log = logging.getLogger(__name__)


def on_wait_players_ready(payload: WaitPlayersReady):
    db.update_task_token(payload.gameId, payload.taskToken)


def ask_question(payload: AskQuestion):
    game_id = payload.gameId

    db.update_task_token(game_id, payload.taskToken)
    quizzes = db.get_quizzes('RU')
    log.info(f'Found {len(quizzes)} quizzes')
    quiz: QuizEntity = Random().choice(quizzes)
    log.info(f'Randomly choose quiz {quiz}')
    sheet: FactSheetEntity = db.get_fact_sheet(quiz.factSheet)
    log.info(f'Retrieved fact sheet {sheet}')
    sheet_rows = fact_sheet.load_rows(sheet.fileKey)
    log.info(f'Loaded sheet {sheet.fileKey} of {len(sheet_rows)} rows')
    answer_row, question_rows = _pick_answer_and_questions(sheet_rows, quiz.answerColumn)
    log.info(f'Randomly picked answer {answer_row} and questions {question_rows}')
    all_rows = question_rows + [answer_row]
    Random().shuffle(all_rows)
    question = {
        'question': quiz.question,
        'questionItem': answer_row[quiz.questionColumn],
        'questionHintItem': answer_row[quiz.questionHintColumn] if quiz.questionHintColumn else None,
        'title': quiz.title,
        'answer': answer_row[quiz.answerColumn],
        'answerHint': answer_row[quiz.answerHintColumn] if quiz.answerHintColumn else None,
        'answerOptions': [{
            'answer': row[quiz.answerColumn],
            'hint': row[quiz.answerHintColumn] if quiz.answerHintColumn else None
        }
            for row in all_rows
        ]
    }
    log.info(f'Saving question: {question}')
    db.update_game_question(game_id, question, GameState.ASK_QUESTION)
    broadcast.send_game_state(game_id)


def _pick_answer_and_questions(sheet_rows, answer_column):
    answer_row = Random().choice(sheet_rows)
    question_rows = []
    while len(question_rows) != 3:
        question_row = Random().choice(sheet_rows)
        if question_row[answer_column] != answer_row[answer_column]:
            question_rows.append(question_row)

    return answer_row, question_rows


def _answer_match(player: PlayerEntity, correct_answer: str):
    return correct_answer is not None and correct_answer == player.answer


def show_answer(payload: ShowAnswer):
    game_id = payload.gameId

    game = db.get_game(game_id)
    correct_answer = game.question['answer']
    players = db.get_active_players(game_id)
    no_of_correct_answers = sum([1 for p in players if _answer_match(p, correct_answer)])
    min_answer_time = min([p.answerTime for p in players if _answer_match(p, correct_answer)] or [-1])

    for player in players:
        increment = 0.0
        if _answer_match(player, correct_answer):
            increment += 1.0
            if no_of_correct_answers > 1 and min_answer_time == player.answerTime:
                increment += 0.5
        db.update_player_score(game_id, player.userId, increment)

    for answer_option in game.question['answerOptions']:
        if answer_option.get('answer') == correct_answer:
            answer_option['correct'] = True
    db.update_game_question(game_id, game.question, GameState.SHOW_ANSWER)

    broadcast.send_game_state(game_id)
