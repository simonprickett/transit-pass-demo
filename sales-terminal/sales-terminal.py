import os
import redis

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password= os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD']
)

def generateSingleUsePass():
    # Use once, never expires.
    return {
        'passType': 'SINGLE_USE'
    }

def generateTwoHourPass():
    # Use an unlimited amount of times within two hours of first use.
    return {
        'passType': 'TWO_HOUR'
    }

def generateTenTripPass():
    # Use ten times, never expires.
    return {
        'passType': 'TEN_TRIP',
        'tripsRemaining': 10
    }

