import platform
import os
import redis

PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password = os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD'],
    decode_responses = True
)

def playAudio(audioFileName):
    if (platform.system() == 'Darwin'):
        # MacOS testing
        os.system('afplay audio/' + audioFileName + '.mp3')
    else:
        # Assume Linux
        os.system('mpg123 -q audio/' + audioFileName + '.mp3')

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

def waitForCard(confirmingCard = False):
    if (confirmingCard == True):
        playAudio('tap-card-to-confirm')

    return input('Card serial number: ')

def hasExistingPass(cardSerialNumber):
    return r.exists(cardSerialNumber)

def waitForPassSelection():
    print('Select a pass type:')
    print('')
    print('1 - single trip')
    print('2 - two hour unlimited use pass')
    print('3 - ten trip pass')

    playAudio('select-a-pass')

    while (True):
        passType = input('Enter 1, 2 or 3: ')
        if (passType == '1'):
            return PASS_TYPE_SINGLE_USE
        elif (passType == '2'):
            return PASS_TYPE_TWO_HOUR
        elif (passType == '3'):
            return PASS_TYPE_TEN_TRIP

def addPassToCard(cardSerialNumber, newPass):
    # Store in Redis.
    r.hmset(cardSerialNumber, newPass)

    # TODO Send a pubsub to say that a pass was issued.

    passType = newPass.get('passType')

    if (passType == PASS_TYPE_SINGLE_USE):
        playAudio('thank-you-single-trip-pass')
        print('Thanks for buying a single trip pass.')
    elif (passType == PASS_TYPE_TWO_HOUR):
        playAudio('thank-you-two-hour-pass')
        print('Thanks for buying a two hour pass.')
    else:
        playAudio('thank-you-ten-trip-pass')
        print('Thanks for buying a ten trip pass.')

def cardHasPassError():
    playAudio('card-already-has-pass')
    print('This card already has a valid pass associated with it.')

def cardMismatch():
    playAudio('mismatch-cancel')
    print('You presented a different card, transaction canceled.')

while(True):
    # Wait for a card to be presented
    # Get the serial number from the card
    cardSerialNumber = waitForCard()

    # Check if this card has a pass on it already...
    if (hasExistingPass(cardSerialNumber)):
        # Cannot add more than one pass to a card
        cardHasPassError()
    else:
        # Wait for a pass type to be chosen
        passType = waitForPassSelection()

        # Wait for the card to be presented again
        confirmCardSerialNumber = waitForCard(True)

        # Check it is the same card
        if (cardSerialNumber == confirmCardSerialNumber):
            # Associate the pass with the card in Redis
            addPassToCard(cardSerialNumber, generatePass(passType))
        else:
            cardMismatch()