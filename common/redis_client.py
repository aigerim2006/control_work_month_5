import redis
import os

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=6379,
    db=0,
    decode_responses=True
)
