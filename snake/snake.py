import os
import pygame
import time
import sys
import random
import requests
import netifaces

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from email_alerts import sendEmail
from joystick import setup as setupJoystick, cleanUp as cleanUpJoystick, getDirection, Direction
from enum import Enum


class GameState(Enum):
    IDLE = 1,
    PLAYING = 2


os.environ['DISPLAY'] = ':0.0'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

pygame.init()
pygame.display.set_caption('Snake')

white = pygame.Color(255, 255, 255)
green = pygame.Color(000, 255, 000)
black = pygame.Color(000, 000, 000)

gameWindow = pygame.display.set_mode(
    flags=pygame.FULLSCREEN | pygame.NOFRAME | pygame.DOUBLEBUF, depth=16)
windowX, windowY = gameWindow.get_size()
fontName = 'pressstart2p'
font = pygame.font.SysFont(fontName, 22*3)
gameState = GameState.IDLE

# Snake Setup
highScore = 0
snakePosition = [100, 50]
snakeBody = [[100, 50], [90, 50], [80, 50], [70, 50]]
framesPerSecond = pygame.time.Clock()
score = 0
snakeSpeed = 15
fruitSpawn = True
fruitPosition = [random.randrange(1, (windowX // 10)) * 10,
                 random.randrange(1, (windowY // 10)) * 10]

currentDirection = Direction.RIGHT
changeDirectionTo = currentDirection

# Website Setup
print(netifaces.ifaddresses('wlan0')[2][0]["addr"]) 

def getLeaderboard():
    return requests.get('http://127.0.0.1:5000/leaderboard').json()

try:
    highScore = getLeaderboard()["result"]["1"]
except:
    print("Unable To Set High Score Server Might Be Down")

# LCD Setup
PCF8574_address = 0x27

try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

mcp.output(3, 1)
lcd.begin(16, 2)


def sendScore():
    global score
    requests.put('http://127.0.0.1:5000/score/add', json={"score": score})


def resetVariables():
    global snakePosition, snakeBody, fruitSpawn, fruitPosition, score, snakeSpeed, currentDirection, changeDirectionTo, gameState
    score = 0
    fruitSpawn = True
    snakePosition = [100, 50]
    snakeBody = [[100, 50], [90, 50], [80, 50], [70, 50]]
    fruitPosition = [random.randrange(1, (windowX // 10)) * 10,
                     random.randrange(1, (windowY // 10)) * 10]
    currentDirection = Direction.RIGHT
    changeDirectionTo = currentDirection
    gameState = GameState.IDLE


def displayScore():
    global fontName

    font = pygame.font.SysFont(fontName, 10*3)
    surface = font .render('Score: ' + str(score), True, white)
    rect = surface.get_rect()
    rect.topleft = (15, 15)

    gameWindow.blit(surface, rect)


def displayGameOver():
    global fontName, highScore

    font = pygame.font.SysFont(fontName, 22*3)
    surface = font.render(
        'Final Score: ' + str(score), True, white)
    rect = surface.get_rect()
    rect.midtop = (windowX / 2, windowY / 2.5)

    gameWindow.blit(surface, rect)
    pygame.display.flip()
    time.sleep(2)

    try:
        sendScore()
        if score > highScore:
            highScore = score
            sendEmail()
    except:
        print('Unable To Send Score Server Is Probably Down')

    displayMainMenu()
    resetVariables()


def handleSnakeGame():
    global snakePosition, snakeBody, fruitSpawn, fruitPosition, score, snakeSpeed, currentDirection, changeDirectionTo, gameState

    handleDirection()
    if snakePosition[0] == fruitPosition[0] and snakePosition[1] == fruitPosition[1]:
        score += 1
        LCDdisplayScore()
        fruitSpawn = False
    else:
        snakeBody.pop()

    if not fruitSpawn:
        fruitPosition = [random.randrange(
            1, (windowX//10)) * 10, random.randrange(1, (windowY // 10)) * 10]

    fruitSpawn = True
    gameWindow.fill(black)

    for pos in snakeBody:
        pygame.draw.rect(gameWindow, green,
                         pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(gameWindow, '#e8481d', pygame.Rect(
        fruitPosition[0], fruitPosition[1], 10, 10))

    checkGameOver()
    displayScore()


def checkGameOver():
    global snakePosition

    if snakePosition[0] < 0 or snakePosition[0] > windowX-10:
        displayGameOver()

    if snakePosition[1] < 0 or snakePosition[1] > windowY-10:
        displayGameOver()

    for block in snakeBody[1:]:
        if snakePosition[0] == block[0] and snakePosition[1] == block[1]:
            displayGameOver()


def handleDirection():
    global currentDirection
    global changeDirectionTo

    match getDirection():
        case Direction.UP:
            changeDirectionTo = Direction.UP
        case Direction.DOWN:
            changeDirectionTo = Direction.DOWN
        case Direction.LEFT:
            changeDirectionTo = Direction.LEFT
        case Direction.RIGHT:
            changeDirectionTo = Direction.RIGHT

    # Makes Sure That The Snake Can't Change Direction To The Opposite Direction Of 
    # That That It Is Already Going In.
    if changeDirectionTo == Direction.UP and currentDirection != Direction.DOWN:
        currentDirection = Direction.UP
    elif changeDirectionTo == Direction.DOWN and currentDirection != Direction.UP:
        currentDirection = Direction.DOWN
    elif changeDirectionTo == Direction.LEFT and currentDirection != Direction.RIGHT:
        currentDirection = Direction.LEFT
    elif changeDirectionTo == Direction.RIGHT and currentDirection != Direction.LEFT:
        currentDirection = Direction.RIGHT

    match currentDirection:
        case Direction.UP:
            snakePosition[1] -= 10
        case Direction.DOWN:
            snakePosition[1] += 10
        case Direction.LEFT:
            snakePosition[0] -= 10
        case Direction.RIGHT:
            snakePosition[0] += 10

    snakeBody.insert(0, list(snakePosition))


def displayMainMenu():
    gameWindow.fill(black)
    surface = font.render('Press The Screen To Start', True, white)

    rect = surface.get_rect()
    rect.center = (windowX // 2, windowY // 2)

    gameWindow.blit(surface, rect)
    pygame.display.update()


def LCDdisplayScore():
    global score
    global lcd
    lcd.setCursor(0, 0)
    lcd.message('Score: ' + str(score))


def playGame():
    global fontName, gameWindow, windowX, windowY, framesPerSecond, score, snakeSpeed, snakePosition, snakeBody, fruitPosition, fruitSpawn, currentDirection, changeDirectionTo, gameState, lcd

    try:
        lcd.setCursor(0, 0)
        lcd.message('Score: ' + str(score))
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if gameState == GameState.IDLE:
                        gameState = GameState.PLAYING

            match gameState:
                case GameState.IDLE: displayMainMenu(),
                case GameState.PLAYING: handleSnakeGame(),

            pygame.display.update()
            framesPerSecond.tick(snakeSpeed)

    except KeyboardInterrupt:
        cleanUpJoystick()
        lcd.clear()
        pygame.quit()
        sys.exit()
        quit()


setupJoystick()
playGame()
