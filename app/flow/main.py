from common.model import StartGamePayload, parse_sf_payload


def handler(event, _):
    payload: StartGamePayload = parse_sf_payload(event)
    print(payload)
