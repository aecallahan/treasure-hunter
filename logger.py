import os
import tailer
import json
import pyautogui
import time

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

# works for ubuntu
# filePath = os.path.join(os.sep, "mnt", "c", "Users", "Andrew Callahan", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", "Player.log")

# works for windows
filePath = os.path.join("..", "..", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", "Player.log")

class GameStateObject:
    def __init__(self):
        self.hand = []
        self.yard = []
        self.lands = 0

class Point:
    def __init(self, x: int, y: int):
        self.x = x
        self.y = y

def concede():
    pyautogui.click(x=2515, y=45)
    pyautogui.moveTo(x=1280, y=854, duration=0.5)
    time.sleep(0.5)
    pyautogui.click(x=1280, y=854)

def pickCardsAfterMulligan(game: GameStateObject, mullCount: int):
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
        if BASIC_ISLAND in game.hand:
            game.hand.remove(BASIC_ISLAND)
        elif LONELY_SANDBAR in game.hand:
            game.hand.remove(LONELY_SANDBAR)
        elif MYSTIC_SANCTUARY in game.hand:
            game.hand.remove(MYSTIC_SANCTUARY)
        else:
            game.hand.pop(0)
    time.sleep(0.1)
    pyautogui.click(x=1286, y=1158)


def playCard(position: int, game: GameStateObject):
    # Play card at 0-indexed position, left to right
    leftmostXCoordinate = COORDINATES_LIST[len(game.hand)][0][0]
    rightmostXCoordinate = COORDINATES_LIST[len(game.hand)][1][0]
    leftBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / (len(game.hand) + 1) * position) + leftmostXCoordinate
    rightBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / (len(game.hand) + 1) * (position) + 1) + leftmostXCoordinate
    centerOfCard = (leftBoundaryOfCard + rightBoundaryOfCard) / 2
    centerOfCardPosition = (centerOfCard, 1400)
    centerOfScreen = (1280, 720)
    pyautogui.moveTo(centerOfCardPosition, duration=0.5)
    pyautogui.dragTo(centerOfScreen, duration=0.5)
    game.hand.pop(position)


def parseLog(jsonLog: dict, game: GameStateObject):
    try:
        gameState = jsonLog["greToClientEvent"]["greToClientMessages"][0]["gameStateMessage"]
    except KeyError:
        return
    try:
        playerState = gameState["players"][0]
        maxHandSize = playerState["maxHandSize"]
        mulliganCount = playerState.get("mulliganCount", 0)
        currentHandSize = maxHandSize - mulliganCount

        # Warning: this might skip important info?
        if "zones" not in gameState:
            return

        if gameState["zones"][0]["ownerSeatId"] == 1:
            idsOfCardsInHand = set(gameState["zones"][0]["objectInstanceIds"])

        playerHand = []
        for gameObject in gameState["gameObjects"]:
            if gameObject["instanceId"] in idsOfCardsInHand:
                playerHand.append(cardIdNames[gameObject["name"]])

        # TODO: fix key error for 'pendingMessageType' when mulliganing all the way to 0
        mulliganIsPending = playerState["pendingMessageType"] == "ClientMessageType_MulliganResp"
        if mulliganIsPending:
            print(f"currently mulliganing to {currentHandSize} cards")

        print(f"player hand: {playerHand}")
        print()
        # Need extra delay if it's the first hand of the game
        if currentHandSize == 7:
            time.sleep(7)
        time.sleep(1)
        if TREASURE_HUNT not in playerHand:
            pyautogui.click(x=1055, y=1166)
        else:
            pyautogui.click(x=1518, y=1166)
            game.hand = playerHand
            pickCardsAfterMulligan(game, mulliganCount)
            time.sleep(0.5)
            playCard(0, game)
            # concede()
    except KeyError:
        print("Encountered key error")
        # print("Current log:")
        # print(json.dumps(jsonLog, indent=2))




# import pdb; pdb.set_trace()
game = GameStateObject()
for line in tailer.follow(open(filePath)):
    if line.startswith('{ "transactionId"'):
        log = json.loads(line)
        parseLog(log, game)
        # print(json.dumps(log, indent=2))


