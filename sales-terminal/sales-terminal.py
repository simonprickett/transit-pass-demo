import json
import platform
import os
import redis
import RPi.GPIO as GPIO
import SimpleMFRC522

PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

GPIO_ONE_TRIP=19
GPIO_TEN_TRIP=13
GPIO_TWO_HOUR=26

# Connect to Redis Instance
r = redis.Redis(
    host = os.environ['TRANSIT_PASS_DEMO_REDIS_HOST'],
    port = os.environ['TRANSIT_PASS_DEMO_REDIS_PORT'],
    password = os.environ['TRANSIT_PASS_DEMO_REDIS_PASSWORD'],
    decode_responses = True
)

# Configure GPIO for buttons
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GPIO_ONE_TRIP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_TEN_TRIP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_TWO_HOUR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up card reader
cardReader = SimpleMFRC522.SimpleMFRC522()

def readFromCardReader():
  print('Waiting for a card to be presented.')
  id, text = cardReader.read()

  cardSerialNumber = str(id)
  print('Card ' + cardSerialNumber + ' presented.')
  return cardSerialNumber

def waitForButton():
    oneTrip = True
    tenTrip = True
    twoHour = True
    
    while (oneTrip and tenTrip and twoHour):
        oneTrip = GPIO.input(GPIO_ONE_TRIP)
        tenTrip = GPIO.input(GPIO_TEN_TRIP)
        twoHour = GPIO.input(GPIO_TWO_HOUR)

        if (oneTrip == False):
            print('One trip button pressed.')
            return GPIO_ONE_TRIP
        elif (tenTrip == False):
            print('Ten trip button pressed.')
            return GPIO_TEN_TRIP
        elif (twoHour == False):
            print('Two hour button pressed.')
            return GPIO_TWO_HOUR

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

    return readFromCardReader()

def hasExistingPass(cardSerialNumber):
    return r.exists(cardSerialNumber)

def waitForPassSelection():
    print('Waiting for user to press a button.')
    playAudio('select-a-pass')
    passType = waitForButton()
    
    if (passType == GPIO_ONE_TRIP):
        return PASS_TYPE_SINGLE_USE
    elif (passType == GPIO_TWO_HOUR):
        return PASS_TYPE_TWO_HOUR
    elif (passType == GPIO_TEN_TRIP):
        return PASS_TYPE_TEN_TRIP

def addPassToCard(cardSerialNumber, newPass):
    # Store in Redis.
    r.hmset(cardSerialNumber, newPass)

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

    # Publish a message saying that a pass was issued.
    msgPayload = {
        'cardSerialNumber': cardSerialNumber,
        'pass': newPass
    }

    r.publish('pass-issued:' + passType, json.dumps(msgPayload, separators=(',', ':')))

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
