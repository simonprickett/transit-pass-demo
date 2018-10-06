import os
import redis
import time

PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password= os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD']
)

def waitForCard():
    return input('Card serial number: ')

def getPassForCard(cardSerialNumber):
    return r.hgetall(cardSerialNumber)

def updatePass(cardSerialNumber, cardPass):
    # TODO will depend on pass type...
    return

while(True):
    # Set the light to red
    print("Light: Red")

    # Wait for a card to be presented
    cardSerialNumber = waitForCard()

    # Does this card have a pass associated with it?
    cardPass = getPassForCard(cardSerialNumber)

    if (cardPass):
        # Update this card's pass
        updatePass(cardSerialNumber, cardPass)

        print("Light: Solid Green")
        time.sleep(5)
    else:
        print("Light: Flashing Red")
        time.sleep(3)

