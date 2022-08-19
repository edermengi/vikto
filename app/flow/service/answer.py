import logging
from typing import List

from common.model import ShowAnswer
from common.service import broadcast
from common.storage import db
from common.storage.db import PlayerEntity, GameState, GameEntity, QuizType

log = logging.getLogger(__name__)


def _answer_match(player: PlayerEntity, correct_answer: str):
    return correct_answer is not None and correct_answer == player.answer


class SelectOneChecker:

    def __init__(self, game: GameEntity, players: List[PlayerEntity]):
        self.game = game
        self.players = players

    def update_results(self):
        correct_answer = self.game.question['answer']

        no_of_correct_answers = sum([1 for p in self.players if _answer_match(p, correct_answer)])
        min_answer_time = min([p.answerTime for p in self.players if _answer_match(p, correct_answer)] or [-1])

        log.info(f'Calculate scores for {self.players}')
        for player in self.players:
            increment = 0.0
            if _answer_match(player, correct_answer):
                log.info(f'Player {player.userId} answered correctly')
                increment += 1.0
                if no_of_correct_answers > 1 and min_answer_time == player.answerTime:
                    log.info(f'Player {player.userId} answered first')
                    increment += 0.5
            db.update_player_score(self.game.gameId, player.userId, increment)

        for answer_option in self.game.question['answerOptions']:
            if answer_option.get('answer') == correct_answer:
                answer_option['correct'] = True
            answer_no = 0
            for player in self.players:
                answer_no += 1 if _answer_match(player, answer_option.get('answer')) else 0
            answer_option['answerNo'] = answer_no

        return self.game.question


class TypeOneChecker:

    def __init__(self, game: GameEntity, players: List[PlayerEntity]):
        self.game = game
        self.players = players

    def update_results(self):
        correct_answer = self.game.question['answer']

        no_of_correct_answers = sum([1 for p in self.players if _answer_match(p, correct_answer)])
        min_answer_time = min([p.answerTime for p in self.players if _answer_match(p, correct_answer)] or [-1])

        log.info(f'Calculate scores for {self.players}')
        for player in self.players:
            increment = 0.0
            if _answer_match(player, correct_answer):
                log.info(f'Player {player.userId} answered correctly')
                increment += 1.0
                if no_of_correct_answers > 1 and min_answer_time == player.answerTime:
                    log.info(f'Player {player.userId} answered first')
                    increment += 0.5
            db.update_player_score(self.game.gameId, player.userId, increment)
        answers = [{
            'answer': p.answer,
            'userId': p.userId

        } for p in self.players]
        self.game.question['answers'] = answers
        return self.game.question


def show_answer(payload: ShowAnswer):
    game_id = payload.gameId

    log.info(f'Calculate scores for game {game_id}')
    game = db.get_game(game_id)
    players = db.get_active_players(game_id)

    quiz_type = game.question['quizType']
    if quiz_type == QuizType.SELECT_ONE:
        checker = SelectOneChecker(game, players)
    elif quiz_type == QuizType.TYPE_ONE:
        checker = TypeOneChecker(game, players)
    else:
        raise ValueError(f'Unsupported quiz type {quiz_type}')

    question = checker.update_results()

    log.info(f'Update game state and answer results')
    db.update_game(game_id,
                   question=question,
                   gameState=GameState.SHOW_ANSWER)
    log.info(f'Broadcast results')
    broadcast.send_game_state(game_id)
    return {
        'remainingRounds': game.totalNumberOfRounds - game.roundNo,
        'remainingQuestions': game.totalNumberOfQuestions - game.questionNo}
