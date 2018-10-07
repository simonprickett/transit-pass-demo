import json
import platform
import os
import redis
import RPi.GPIO as GPIO
import time

PASS_TYPE_SINGLE_USE = 'SINGLE_USE'
PASS_TYPE_TWO_HOUR = 'TWO_HOUR'
PASS_TYPE_TEN_TRIP = 'TEN_TRIP'

# GPIO Pins for the traffic light LEDs
RED = 19
YELLOW=13
GREEN = 26

# Seconds in two hours used when activating two hour pass
TWO_HOURS = 60 * 60 * 2

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

def sendMessage(topic, msgPayload):
    print('sending to topic "' + topic + '"')
    print(json.dumps(msgPayload, separators=(',', ':')))
    r.publish(topic, json.dumps(msgPayload, separators=(',', ':')))

def waitForCard():
    return input('Card serial number: ')

def getPassForCard(cardSerialNumber):
    return r.hgetall(cardSerialNumber)

def updatePass(cardSerialNumber, cardPass):
    passType = cardPass.get('passType')

    if (passType == PASS_TYPE_SINGLE_USE):
        # This is the only use allowed for this pass so delete it from Redis
        r.delete(cardSerialNumber)

        # Report this pass was used
        print('Single use pass used and deleted.')
    elif (passType == PASS_TYPE_TWO_HOUR):
        # Check if this is first use and start expiring the pass if so...
        # Nothing to do except report this pass was used for a journey

        passTtl = r.ttl(cardSerialNumber)

        if (not passTtl):
            print('Two hour pass first use, setting time to live.')

            r.expire(cardSerialNumber, TWO_HOURS)
            sendMessage('pass-activated:' + PASS_TYPE_TWO_HOUR, {
                'cardSerialNumber': cardSerialNumber,
                'pass': cardPass,
                'remainingTime': TWO_HOURS  
            })
        else:
            print('Two hour pass has ' + str(round((passTtl / 60), 1)) + ' minutes remaining.')

        sendMessage('pass-used:' + PASS_TYPE_TWO_HOUR, {
            'cardSerialNumber': cardSerialNumber,
            'pass': cardPass,
            'remainingTime': passTtl  
        })
    else:
        # Ten trip pass, delete one from the number of remaining trips, delete from Redis if 0
        tripsRemaining = cardPass.get('tripsRemaining')

        # Note tripsRemaining comes back as a String
        if (tripsRemaining == '1'):
            # Final trip for this pass, so delete this key
            r.delete(cardSerialNumber)
            print('This ten trip pass has no more trips remaining, deleted it.')

            # Report that this pass used up all of its trips
        else:
            # TODO hincr by -1 this field
            r.hincrby(cardSerialNumber, 'tripsRemaining', -1)

            newTripsRemaining = (int(tripsRemaining) - 1)

            print('This ten trip pass has ' + str(newTripsRemaining) + ' more trips remaining.')
            # Report that this pass was used and has trips remaining

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)

GPIO.output(YELLOW, False)

while(True):
    # Set the light to red
    print('Light: Red')
    GPIO.output(RED, True)
    GPIO.output(GREEN, False)

    # Wait for a card to be presented
    cardSerialNumber = waitForCard()

    # Does this card have a pass associated with it?
    cardPass = getPassForCard(cardSerialNumber)

    if (cardPass):
        # Update this card's pass
        updatePass(cardSerialNumber, cardPass)

        playAudio('access-granted')
        print('Light: Solid Green')
        GPIO.output(RED, False)
        GPIO.output(GREEN, True)
        time.sleep(5)
    else:
        # TODO Send a pubsub for invalid use of card...
        print('Light: Flashing Red')
        playAudio('access-denied')
        GPIO.output(RED, False)
        time.sleep(0.5)
        GPIO.output(RED, True)
        time.sleep(0.5)
        GPIO.output(RED, False)
        time.sleep(0.5)
        GPIO.output(RED, True)
        time.sleep(0.5)
        GPIO.output(RED, False)
        time.sleep(2)
