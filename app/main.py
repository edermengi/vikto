from common.model import WsApiRequest
from storage import db


def handler(event, context):
    req = WsApiRequest.parse(event)
    print(req)
    if req.route_key == '$connect':
        db.create_session(req.connection_id, req.source_ip, req.connected_at)
        return {'statusCode': 200, 'body': 'Connected.'}
    elif req.route_key == '$disconnect':
        db.close_session(req.connection_id)
        return {'statusCode': 200, 'body': 'Disconnected.'}
    elif req.route_key == '$default':
        return {'statusCode': 200, 'body': 'Default'}
    else:
        raise Exception(f'Unexpected route of {req.route_key}')
