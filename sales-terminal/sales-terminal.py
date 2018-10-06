import os
import redis

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password= os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD']
)
