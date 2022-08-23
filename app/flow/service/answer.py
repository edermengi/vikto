import logging
from decimal import Decimal
from typing import List

from common.model import ShowAnswer
from common.service import broadcast
from common.storage import db, util
from common.storage.db import PlayerEntity, GameState, GameEntity, QuizType
from common.storage.db_util import Add
from flow.service import lev

log = logging.getLogger(__name__)


def _answer_match(player: PlayerEntity, correct_answer: str):
    return correct_answer is not None and \
           player.answer is not None and \
           correct_answer.upper() == player.answer.upper()


class SelectOneChecker:

    def __init__(self, game: GameEntity, players: List[PlayerEntity]):
        self.game = game
        self.players = players
        self.wait_seconds = 5

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
            db.update_player(self.game.gameId, player.userId,
                             score=Add(Decimal(increment)), answer=None, answerTime=None)

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
        self.wait_seconds = 20

    def update_results(self):
        correct_answer = self.game.question['answer'].upper()

        min_answer_time = min([p.answerTime for p in self.players if p.answerTime] or [-1])

        log.info(f'Calculate scores for game {self.game.gameId} and correct answer {correct_answer}')
        player_answers = []
        for player in self.players:
            player_answer = player.answer.upper() if player.answer else None
            increment = lev.lev_percentage(correct_answer, player_answer) * 2
            log.info(f'Players score fo the answer {player_answer} is  {increment}')

            if len(self.players) > 1 and min_answer_time == player.answerTime:
                log.info(f'Player {player.userId} answered first')
                increment += 0.5

            dec_incr = Decimal(format(increment, '.2g'))
            db.update_player(self.game.gameId, player.userId,
                             score=Add(dec_incr), answer=None, answerTime=None)
            player_answers.append({
                'answer': player_answer,
                'userId': player.userId,
                'score': dec_incr
            })

        self.game.question['playerAnswers'] = player_answers
        return self.game.question


class TypeOneFromSetChecker:

    def __init__(self, game: GameEntity, players: List[PlayerEntity]):
        self.game = game
        self.players = players
        self.wait_seconds = 20

    def update_results(self):
        correct_answer = self.game.question['answer'].upper()
        correct_answers = correct_answer.split(',')

        min_answer_time = min([p.answerTime for p in self.players if p.answerTime] or [-1])

        log.info(f'Calculate scores for game {self.game.gameId} and correct answer {correct_answer}')
        player_answers = []
        for player in self.players:
            player_answer = player.answer.upper() if player.answer else None
            best_match = None
            best_score = 0.0
            for correct_answer in correct_answers:
                score = lev.lev_percentage(correct_answer, player_answer) * 2
                log.info(f'Players score fo the answer {player_answer} and {correct_answer} is {score}')
                if score > best_score:
                    best_score = score
                    best_match = correct_answer

            if len(self.players) > 1 and min_answer_time == player.answerTime:
                log.info(f'Player {player.userId} answered first')
                best_score += 0.5

            dec_incr = Decimal(format(best_score, '.2g'))
            db.update_player(self.game.gameId, player.userId,
                             score=Add(dec_incr), answer=None, answerTime=None)
            player_answers.append({
                'answer': player_answer,
                'bestMatch': best_match,
                'userId': player.userId,
                'score': dec_incr
            })

        self.game.question['playerAnswers'] = player_answers
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
    elif quiz_type == QuizType.TYPE_ONE_FROM_SET:
        checker = TypeOneFromSetChecker(game, players)
    else:
        raise ValueError(f'Unsupported quiz type {quiz_type}')

    question = checker.update_results()

    log.info(f'Update game state and answer results')
    db.update_game(game_id,
                   question=question,
                   gameState=GameState.SHOW_ANSWER,
                   timerStart=util.now_timestamp(),
                   timerSeconds=checker.wait_seconds)
    log.info(f'Broadcast results')
    broadcast.send_game_state(game_id)
    return {
        'remainingRounds': game.totalNumberOfRounds - game.roundNo,
        'remainingQuestions': game.totalNumberOfQuestions - game.questionNo,
        'waitSeconds': checker.wait_seconds
    }
