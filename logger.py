import os
import tailer
import json
import pyautogui
import time

from PIL import ImageGrab

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"
RAUGRIN_TRIOME = "Raugrin Triome"

cardIdNames = {
    652: BASIC_ISLAND,
    10826: LONELY_SANDBAR,
    24877: TREASURE_HUNT,
    414466: MYSTIC_SANCTUARY,
    419870: THASSAS_ORACLE,
    428659: RAUGRIN_TRIOME
}

LEFTMOST_CARD_WITH_EIGHT_CARDS = (385, 1439)
RIGHTMOST_CARD_WITH_EIGHT_CARDS = (2130, 1439)

LEFTMOST_CARD_WITH_SEVEN_CARDS = (470, 1419)
RIGHTMOST_CARD_WITH_SEVEN_CARDS = (2096, 1423)

LEFTMOST_CARD_WITH_SIX_CARDS = (553, 1355)
RIGHTMOST_CARD_WITH_SIX_CARDS = (1987, 1376)

LEFTMOST_CARD_WITH_FIVE_CARDS = (698, 1409)
RIGHTMOST_CARD_WITH_FIVE_CARDS = (1865, 1413)

LEFTMOST_CARD_WITH_FOUR_CARDS = (807, 1392)
RIGHTMOST_CARD_WITH_FOUR_CARDS = (1748, 1413)

# The rest of these coordinates are just estimates
LEFTMOST_CARD_WITH_THREE_CARDS = (920, 1392)
RIGHTMOST_CARD_WITH_THREE_CARDS = (1610, 1413)

LEFTMOST_CARD_WITH_TWO_CARDS = (1100, 1392)
RIGHTMOST_CARD_WITH_TWO_CARDS = (1480, 1413)

LEFTMOST_CARD_WITH_ONE_CARDS = (1250, 1392)
RIGHTMOST_CARD_WITH_ONE_CARDS = (1310, 1413)

COORDINATES_LIST = [
[],
[LEFTMOST_CARD_WITH_ONE_CARDS,
RIGHTMOST_CARD_WITH_ONE_CARDS],
[LEFTMOST_CARD_WITH_TWO_CARDS,
RIGHTMOST_CARD_WITH_TWO_CARDS],
[LEFTMOST_CARD_WITH_THREE_CARDS,
RIGHTMOST_CARD_WITH_THREE_CARDS],
[LEFTMOST_CARD_WITH_FOUR_CARDS,
RIGHTMOST_CARD_WITH_FOUR_CARDS],
[LEFTMOST_CARD_WITH_FIVE_CARDS,
RIGHTMOST_CARD_WITH_FIVE_CARDS],
[LEFTMOST_CARD_WITH_SIX_CARDS,
RIGHTMOST_CARD_WITH_SIX_CARDS],
[LEFTMOST_CARD_WITH_SEVEN_CARDS,
RIGHTMOST_CARD_WITH_SEVEN_CARDS],
[LEFTMOST_CARD_WITH_EIGHT_CARDS,
RIGHTMOST_CARD_WITH_EIGHT_CARDS],
]

NEXT_BUTTON_POSITION = (2367, 1266)

# works for windows
filePath = os.path.join("..", "..", "..", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", "Player.log")

class GameStateObject:
    def __init__(self):
        self.hand = []
        self.yard = []
        self.lands = 0
        self.tappedLands = 0
        self.landForTurn = False

class Point:
    def __init(self, x: int, y: int):
        self.x = x
        self.y = y

def mouseConcede():
    print("conceding")
    pyautogui.click(x=2515, y=45)
    pyautogui.moveTo(x=1280, y=854, duration=0.5)
    time.sleep(0.5)
    pyautogui.click(x=1280, y=854)

def mousePlayLonelySandbar():
    time.sleep(0.5)
    pyautogui.click(x=951, y=652)

def mousePickCardsAfterMulligan(mullCount: int, game: GameStateObject):
    BOTTOM_OF_LIBRARY_POS = (346, 750)
    SEVENTH_CARD_POS = (1199, 655)
    SIXTH_CARD_POS = (1240, 647)
    FIFTH_CARD_POS = (1359, 724)
    FOURTH_CARD_POS = (1448, 682)
    THIRD_CARD_POS = (1560, 693)
    SECOND_CARD_POS = (1620, 693)
    positions = [
        SEVENTH_CARD_POS,
        SIXTH_CARD_POS,
        FIFTH_CARD_POS,
        FOURTH_CARD_POS,
        THIRD_CARD_POS,
        SECOND_CARD_POS,
    ]

    for i in range(mullCount):
        position = positions.pop(0)
        pyautogui.moveTo(position, duration=0.5)
        pyautogui.dragTo(BOTTOM_OF_LIBRARY_POS, duration=0.5)
        puttingOnBottom = game.hand.pop(0)

        print(f"putting {puttingOnBottom} on bottom")
    print(f"hand after mulligan: {game.hand}")
    time.sleep(0.1)
    pyautogui.click(x=1286, y=1158)

def mouseMulligan(mullCount: int):
    # Need extra delay if it's the first hand of the game
    if mullCount == 0:
        time.sleep(7)
    time.sleep(1)
    pyautogui.click(x=1055, y=1166)

def mouseKeepHand(mullCount: int, game: GameStateObject):
    # Need extra delay if it's the first hand of the game
    if mullCount == 0:
        time.sleep(7)
    time.sleep(1)
    pyautogui.click(x=1518, y=1166)
    mousePickCardsAfterMulligan(mullCount, game)


def decideMulligan(gameState: dict, game: GameStateObject):
    # print(json.dumps(gameState, indent=2))
    player = gameState["gameStateMessage"]["players"][0]
    mulliganCount = player.get("mulliganCount", 0)
    currentHandSize = player["maxHandSize"] - mulliganCount
    print(f"currently mulliganing to {currentHandSize} cards")

    handZone = gameState["gameStateMessage"]["zones"][0]
    # Defensive checks because not sure first zone is always p1's hand
    if handZone["type"] != "ZoneType_Hand":
        print("Error: handZone was not first zone")
    if handZone["visibility"] != "Visibility_Private":
        print("Error: handZone was not Visibility_Private")
    if handZone["ownerSeatId"] != 1:
        print("Error: handZone wasn't owned by player 1")

    idsOfCardsInHand = set(handZone["objectInstanceIds"])
    playerHand = []
    for gameObject in gameState["gameStateMessage"]["gameObjects"]:
        if gameObject["instanceId"] in idsOfCardsInHand:
            playerHand.append(cardIdNames[gameObject["name"]])

    if TREASURE_HUNT not in playerHand:
        if currentHandSize == 1:
            mouseConcede()
        else:
            mouseMulligan(mulliganCount)
    else:
        # Sorting alphabetically puts hand in same order as client, left to right
        playerHand.sort()
        game.hand = playerHand
        print(f"keeping hand: {game.hand}")
        mouseKeepHand(mulliganCount, game)


def isPlayerStep(step: str, log: dict) -> bool:
    for clientMessage in log["greToClientEvent"]["greToClientMessages"]:
        if clientMessage.get("gameStateMessage", {}).get("turnInfo", {}).get("step") == step \
          and clientMessage["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            return True
    return False

def isPlayerPhase(phase: str, log: dict) -> bool:
    for clientMessage in log["greToClientEvent"]["greToClientMessages"]:
        if clientMessage.get("gameStateMessage", {}).get("turnInfo", {}).get("phase") == phase \
          and clientMessage["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            return True
    return False

def updateHandWithDraw(log: dict, game: GameStateObject):
    for clientMessage in log["greToClientEvent"]["greToClientMessages"]:
        if "gameObjects" in clientMessage.get("gameStateMessage", {}) and \
          clientMessage["gameStateMessage"]["gameObjects"][0]["ownerSeatId"] == 1:
            game.hand.append(cardIdNames[clientMessage["gameStateMessage"]["gameObjects"][0]["name"]])
            print(f"hand after draw: {game.hand}")


def mousePlayCard(position: int, game: GameStateObject):
    # Play card at 0-indexed position, left to right
    time.sleep(3)
    leftmostXCoordinate = COORDINATES_LIST[len(game.hand)][0][0]
    rightmostXCoordinate = COORDINATES_LIST[len(game.hand)][1][0]
    leftBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / len(game.hand) * position) + leftmostXCoordinate
    rightBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / len(game.hand) * (position + 1)) + leftmostXCoordinate
    centerOfCard = (leftBoundaryOfCard + rightBoundaryOfCard) / 2
    centerOfCardPosition = (centerOfCard, 1400)
    centerOfScreen = (1280, 720)
    # import pdb; pdb.set_trace()
    pyautogui.moveTo(centerOfCardPosition, duration=0.5)
    pyautogui.dragTo(centerOfScreen, duration=0.5)
    cardPlayed = game.hand.pop(position)
    if cardPlayed == LONELY_SANDBAR:
        mousePlayLonelySandbar()

def identifyMulliganMessage(log: dict) -> dict:
    for clientMessage in log["greToClientEvent"]["greToClientMessages"]:
        if clientMessage["type"] != "GREMessageType_GameStateMessage":
            continue
        else:
            # print("inspecting clientMessage:")
            # print(json.dumps(clientMessage, indent=2))
            if "gameStateMessage" in clientMessage and \
              "players" in clientMessage["gameStateMessage"] and \
              clientMessage["gameStateMessage"]["players"][0].get("pendingMessageType") \
              == "ClientMessageType_MulliganResp":
                return clientMessage
    return None

def playIsland(game: GameStateObject):
    if BASIC_ISLAND not in game.hand:
        return
    print("playing island")
    print(f"hand before playing: {game.hand}")
    index = game.hand.index(BASIC_ISLAND)
    print(f"playing card at position {index}")
    mousePlayCard(index, game)
    game.landForTurn = True
    game.lands += 1

def playTreasureHunt(game: GameStateObject):
    print("playing treasure hunt")
    print(f"hand before playing: {game.hand}")
    index = game.hand.index(TREASURE_HUNT)
    print(f"playing card at position {index}")
    mousePlayCard(index, game)
    game.tappedLands += 2
    game.yard.append(TREASURE_HUNT)


def takeGameAction(jsonLog: dict, game: GameStateObject):
    if "greToClientEvent" not in jsonLog:
        return
    mullMessage = identifyMulliganMessage(jsonLog)
    if mullMessage:
        decideMulligan(mullMessage, game)
    else:
        if isPlayerStep("Step_Draw", jsonLog):
            print("drawing card")
            updateHandWithDraw(jsonLog, game)
            game.landForTurn = False
            game.tappedLands = 0
        # TODO: cards are being played from wrong index
        if isPlayerPhase("Phase_Main1", jsonLog):
            if not game.landForTurn:
                playIsland(game)
            if TREASURE_HUNT in game.hand and game.lands - game.tappedLands >= 2:
                playTreasureHunt(game)


numberOfLogs = 0

game = GameStateObject()
for line in tailer.follow(open(filePath)):
    if line.startswith('{ "transactionId"'):
        numberOfLogs += 1
        print(f"number of logs: {numberOfLogs}")
        log = json.loads(line)
        takeGameAction(log, game)
        # print(json.dumps(log, indent=2))

#Manually run on single log
# with open("opponent_goes_first.json") as file:
#     data = json.load(file)
#     takeGameAction(data, game)
