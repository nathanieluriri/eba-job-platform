import redis
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")

REDIS_PORT = os.getenv("REDIS_PORT")
print(REDIS_HOST)
print(REDIS_PORT)

REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

auth_kwargs = {}
if REDIS_USERNAME:
    auth_kwargs["username"] = REDIS_USERNAME
if REDIS_PASSWORD:
    auth_kwargs["password"] = REDIS_PASSWORD

cache_db = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    **auth_kwargs
)



def cache_with_expiry(key: str, value: str, ttl: int = 60):
    """
    Store a key-value pair in Redis with expiration.

    Args:
        key (str): The Redis key.
        value (str): The value to store.
        ttl (int): Time-to-live in seconds (default 60).
    """
    cache_db.setex(name=key, time=ttl, value=value)
    return f"Key '{key}' set with TTL {ttl}s"

def get_cached_value(key: str):
    value = cache_db.get(key)
    return value