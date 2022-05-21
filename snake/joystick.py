import RPi.GPIO as GPIO
from ADCDevice import PCF8591, ADS7830, ADCDevice
from enum import Enum

joyStickPin = 12
ADCModule = ADCDevice()


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


def setup():
    global ADCModule

    if ADCModule.detectI2C(0x48):
        ADCModule = PCF8591()
    elif ADCModule.detectI2C(0x4b):
        ADCModule = ADS7830()
    else:
        print("Unable to find ADC device, exiting..")
        exit(-1)

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(joyStickPin, GPIO.IN, GPIO.PUD_UP)


def getDirection():
    yAxis = ADCModule.analogRead(0)
    xAxis = ADCModule.analogRead(1)

    # Top Row
    if 0 <= xAxis <= 255 and 0 <= yAxis <= 85:
        return Direction.UP

    # Middle Row
    if 0 <= xAxis <= 85 and 85 <= yAxis <= 170:
        return Direction.LEFT

    if 170 <= xAxis <= 255 and 85 <= yAxis <= 170:
        return Direction.RIGHT

    # Bottom Row
    if 0 <= xAxis <= 255 and 170 <= yAxis <= 255:
        return Direction.DOWN


def cleanUp():
    ADCModule.close()
    GPIO.cleanup()
