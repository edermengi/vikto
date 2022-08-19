from random import Random


def recover_decode_utf8(b: bytes):
    st = 0
    end = 1
    for i in range(3):
        try:
            return b[st:-end].decode('utf-8')
        except UnicodeError as e:
            print(e)
            if e.reason == 'invalid start byte':
                st += 1
            elif e.reason == 'unexpected end of data':
                end += 1
            else:
                raise e
    raise ValueError('Cannot decore string')


def replace_random_letters(text: str, replacement: chr = '.', percentage=0.70):
    num = round(len(text) * percentage)
    random_indexes = Random().sample(range(len(text)), k=num)
    for index in random_indexes:
        text = text[:index] + replacement + text[index + 1:]
    return text
