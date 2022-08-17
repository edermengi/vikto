import secrets
import string

from common.model import NewGameRequest, NewGameResponse, JoinGameRequest, JoinGameResponse, ReadyRequest, \
    ReadyResponse, AnswerRequest, ChooseTopicRequest
from wsapi.service import sfn
from common.service import broadcast
from common.storage import db, util


def random_game_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def new_game(req: NewGameRequest) -> NewGameResponse:
    game_id = random_game_id()
    db.create_game(game_id, req.userId)
    db.join_game(game_id, req.userId)
    broadcast.send_game_state(game_id)
    sfn.start(game_id)

    return NewGameResponse(game_id)


def join_game(req: JoinGameRequest) -> JoinGameResponse:
    game_id = req.gameId
    user_id = req.userId

    db.join_game(game_id, user_id)
    broadcast.send_game_state(game_id)

    return JoinGameResponse(game_id)


def ready(req: ReadyRequest):
    game_id = req.gameId
    user_id = req.userId

    db.update_ready_status(game_id, user_id)
    players = db.get_active_players(game_id)
    ready_no = sum(p.ready for p in players)
    if ready_no >= min(2, len(players)):
        game = db.get_game(game_id)
        sfn.send_task_success(game.taskToken)
        db.update_task_token(game_id, None)
    broadcast.send_game_state(game_id)
    return ReadyResponse()


def answer(req: AnswerRequest):
    game_id = req.gameId
    user_id = req.userId
    answer_ = req.answer

    db.update_player_answer(game_id, user_id, answer_, util.now_timestamp())
    players = db.get_active_players(game_id)
    all_answered = all([p.answer is not None for p in players])
    if all_answered:
        game = db.get_game(game_id)
        sfn.send_task_success(game.taskToken)


def choose_topic(req: ChooseTopicRequest):
    game_id = req.gameId
    user_id = req.userId
    topic = req.topic

    db.update_player_topic_vote(game_id, user_id, topic)
    players = db.get_active_players(game_id)
    all_voted = all([p.topicVote is not None for p in players])
    if all_voted:
        game = db.get_game(game_id)
        sfn.send_task_success(game.taskToken)

    return None
