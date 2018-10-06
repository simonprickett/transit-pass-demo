import os
import redis

PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password= os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD']
)

def generatePass(passType):
    if (passType == PASS_TYPE_SINGLE_USE):
        # Use once, never expires.
        return {
            'passType': PASS_TYPE_SINGLE_USE
        }
    elif (passType == PASS_TYPE_TWO_HOUR):
        # Use an unlimited amount of times within two hours of first use.
        return {
            'passType': PASS_TYPE_TWO_HOUR
        }
    else:
        # Use ten times, never expires.
        return {
            'passType': PASS_TYPE_TEN_TRIP,
            'tripsRemaining': 10
        }

def waitForCard():
    return input('Card serial number: ')

def waitForPassSelection():
    print('Select a pass type:')
    print('')
    print('1 - single trip')
    print('2 - two hour unlmited use pass')
    print('3 - ten trip pass')

    while (True):
        passType = input('Enter 1, 2 or 3: ')
        if (passType == '1'):
            return PASS_TYPE_SINGLE_USE
        elif (passType == '2'):
            return PASS_TYPE_TWO_HOUR
        elif (passType == '3'):
            return PASS_TYPE_TEN_TRIP

def addPassToCard(cardSerialNumber, newPass):
    print('Thank you, your transaction is complete.')

def cardMismatch():
    print('You presented a different card, transaction canceled.')

while(True):
    # Wait for a card to be presented
    # Get the serial number from the card
    cardSerialNumber = waitForCard()

    # TODO Check if this card has a pass on it already...

    # Wait for a pass type to be chosen
    passType = waitForPassSelection()

    # Wait for the card to be presented again
    confirmCardSerialNumber = waitForCard()

    # Check it is the same card
    if (cardSerialNumber == confirmCardSerialNumber):
        # Associate the pass with the card in Redis
        addPassToCard(cardSerialNumber, generatePass(passType))
    else:
        cardMismatch()