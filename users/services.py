import random
from common.redis_client import redis_client


def generate_confirmation_code():
    return str(random.randint(100000, 999999))


def save_confirmation_code(email):
    code = generate_confirmation_code()
    key = f"confirm_code:{email}"
    redis_client.setex(key, 300, code)
    return code

