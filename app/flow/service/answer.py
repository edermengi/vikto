import logging

from common.model import ShowAnswer
from common.service import broadcast
from common.storage import db
from common.storage.db import PlayerEntity, GameState

log = logging.getLogger(__name__)


def show_answer(payload: ShowAnswer):
    game_id = payload.gameId

    log.info(f'Calculate scores for game {game_id}')
    game = db.get_game(game_id)
    correct_answer = game.question['answer']
    players = db.get_active_players(game_id)
    no_of_correct_answers = sum([1 for p in players if _answer_match(p, correct_answer)])
    min_answer_time = min([p.answerTime for p in players if _answer_match(p, correct_answer)] or [-1])

    log.info(f'Calculate scores for {players}')
    for player in players:
        increment = 0.0
        if _answer_match(player, correct_answer):
            log.info(f'Player {player.userId} answered correctly')
            increment += 1.0
            if no_of_correct_answers > 1 and min_answer_time == player.answerTime:
                log.info(f'Player {player.userId} answered first')
                increment += 0.5
        db.update_player_score(game_id, player.userId, increment)

    for answer_option in game.question['answerOptions']:
        if answer_option.get('answer') == correct_answer:
            answer_option['correct'] = True
        answer_no = 0
        for player in players:
            answer_no += 1 if _answer_match(player, answer_option.get('answer')) else 0;
        answer_option['answerNo'] = answer_no

    log.info(f'Update game state and answer results')
    db.update_game(game_id,
                   question=game.question,
                   gameState=GameState.SHOW_ANSWER)
    log.info(f'Broadcast results')
    broadcast.send_game_state(game_id)
    return {
        'remainingRounds': game.totalNumberOfRounds - game.roundNo,
        'remainingQuestions': game.totalNumberOfQuestions - game.questionNo}


def _answer_match(player: PlayerEntity, correct_answer: str):
    return correct_answer is not None and correct_answer == player.answer
