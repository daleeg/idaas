import random

CLIENT_SECRET_GENERATOR_LENGTH = 128
CLIENT_ID_GENERATOR_LENGTH = 40
UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')


def generate_client_pair():
    client_id = generate_client_id(length=CLIENT_ID_GENERATOR_LENGTH, chars=UNICODE_ASCII_CHARACTER_SET)
    client_secret = generate_client_id(length=CLIENT_SECRET_GENERATOR_LENGTH, chars=UNICODE_ASCII_CHARACTER_SET)
    return client_id, client_secret


def generate_client_id(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """Generates an OAuth client_id

    OAuth 2 specify the format of client_id in
    http://tools.ietf.org/html/rfc6749#appendix-A.
    """
    return generate_token(length, chars)


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
