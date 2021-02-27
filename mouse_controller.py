'''
Module handles all mouse actions requested by game player
'''
import time
import pyautogui
from PIL import ImageEnhance, ImageGrab
import pytesseract

from log_crawler import get_newest_log

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"
RAUGRIN_TRIOME = "Raugrin Triome"

LEFTMOST_CARD_WITH_THIRTY_FIVE_CARDS = (392, 1397)
RIGHTMOST_CARD_WITH_THIRTY_FIVE_CARDS = (2136, 1383)

LEFTMOST_CARD_WITH_SIXTEEN_CARDS = (490, 1418)
RIGHTMOST_CARD_WITH_SIXTEEN_CARDS = (2040, 1434)

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
# TODO: delete this
[LEFTMOST_CARD_WITH_EIGHT_CARDS,
RIGHTMOST_CARD_WITH_EIGHT_CARDS],
[LEFTMOST_CARD_WITH_EIGHT_CARDS,
RIGHTMOST_CARD_WITH_EIGHT_CARDS],
]

NEXT_BUTTON_POSITION = (2367, 1266)

def discardToSeven(numberToDiscard: int, game):
    print(f"discarding {numberToDiscard} cards...")
    if numberToDiscard > 18:
        leftmostXCoordinate = LEFTMOST_CARD_WITH_THIRTY_FIVE_CARDS[0]
        rightmostXCoordinate = RIGHTMOST_CARD_WITH_THIRTY_FIVE_CARDS[0]
    else:
        leftmostXCoordinate = LEFTMOST_CARD_WITH_SIXTEEN_CARDS[0]
        rightmostXCoordinate = RIGHTMOST_CARD_WITH_SIXTEEN_CARDS[0]
    handSize = numberToDiscard + 7
    subtractXStart = 150
    addXEnd = 150
    newHand = []
    for position in range(handSize):
        print(f"hover card {position}")
        leftBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / handSize * position) + leftmostXCoordinate
        rightBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / handSize * (position + 1)) + leftmostXCoordinate
        centerOfCard = (leftBoundaryOfCard + rightBoundaryOfCard) / 2
        centerOfCardPosition = (centerOfCard, 1400)
        pyautogui.moveTo(centerOfCardPosition)
        time.sleep(0.2)
        image = ImageGrab.grab(bbox=(centerOfCard - subtractXStart, 874, centerOfCard + addXEnd, 910))
        image = ImageEnhance.Contrast(image).enhance(10)
        image.save(f'test{position}.png')
        cardName = pytesseract.image_to_string(image)
        print(f"read card name: {cardName}")
        if "Mystic" in cardName or "Sanctuary" in cardName:
            newHand.append(MYSTIC_SANCTUARY)
        elif "Treasure" in cardName or "Hunt" in cardName:
            newHand.append(TREASURE_HUNT)
        elif "Thassa" in cardName or "Oracle" in cardName:
            newHand.append(THASSAS_ORACLE)
        else:
            pyautogui.click(centerOfCardPosition)
            numberToDiscard -= 1
            if numberToDiscard == 0:
                while len(newHand) < 7:
                    newHand.append(BASIC_ISLAND)
                game.hand = newHand
                # Click submit
                pyautogui.click(x=2372, y=1267)
                return


def concede():
    print("conceding")
    pyautogui.click(x=2515, y=45)
    pyautogui.moveTo(x=1280, y=854, duration=0.5)
    time.sleep(1)
    pyautogui.click(x=1280, y=854)
    pyautogui.click(x=1280, y=854)
    pyautogui.click(x=1280, y=854)
    pyautogui.click(x=1280, y=854)
    pyautogui.click(x=1280, y=854)

def wait_for_mulligan_priority():
    waiting_for_priority = True
    while waiting_for_priority:
        waiting_for_priority = not look_for_mulligan_button()

def wait_for_main_phase_priority():
    waiting_for_priority = True
    while waiting_for_priority:
        waiting_for_priority = not lookForNextButton()

def playLonelySandbarSecondPrompt():
    time.sleep(0.5)
    pyautogui.click(x=951, y=652)

def mousePickCardsAfterMulligan(mullCount: int, game):
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
        pyautogui.moveTo(position, duration=0.1)
        pyautogui.dragTo(BOTTOM_OF_LIBRARY_POS, duration=0.3)
        puttingOnBottom = game.hand.pop(0)

        print(f"putting {puttingOnBottom} on bottom")
    print(f"hand after mulligan: {game.hand}")
    time.sleep(0.1)
    pyautogui.click(x=1286, y=1158)

def mulligan():
    wait_for_mulligan_priority()
    pyautogui.click(x=1055, y=1166)
    pyautogui.moveTo(x=286, y=1286)

def keepHand(mullCount: int, game):
    wait_for_mulligan_priority()
    pyautogui.click(x=1518, y=1166)
    mousePickCardsAfterMulligan(mullCount, game)


def playCard(position: int, hand_size: int):
    # Play card at 0-indexed position, left to right

    # Do not play card until p1 has priority
    wait_for_main_phase_priority()
    # time.sleep(4)

    leftmostXCoordinate = COORDINATES_LIST[hand_size][0][0]
    rightmostXCoordinate = COORDINATES_LIST[hand_size][1][0]
    leftBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / hand_size * position) + leftmostXCoordinate
    rightBoundaryOfCard = ((rightmostXCoordinate - leftmostXCoordinate) / hand_size * (position + 1)) + leftmostXCoordinate
    centerOfCard = (leftBoundaryOfCard + rightBoundaryOfCard) / 2
    centerOfCardPosition = (centerOfCard, 1400)
    centerOfScreen = (1280, 720)
    # import pdb; pdb.set_trace()
    pyautogui.moveTo(centerOfCardPosition, duration=0.1)
    pyautogui.dragTo(centerOfScreen, duration=0.3)


def lookForNextButton() -> bool:
    image = ImageGrab.grab(bbox=(2313, 1242, 2426, 1289))
    image = ImageEnhance.Contrast(image).enhance(10)
    message = pytesseract.image_to_string(image)
    print(message)
    return "Next" in message

def read_number_of_cards_to_discard() -> int:
    '''Read message in center of screen instructing player to discard to hand size'''
    # TODO: doesn't handle message "Discard a card"
    # TODO: set tesseract config to only read alphanumeric characters
    image = ImageGrab.grab(bbox=(1099, 577, 1430, 635))
    # Increase contrast 10x for better OCR results
    image = ImageEnhance.Contrast(image).enhance(10)
    image.save('output.png')
    message = pytesseract.image_to_string(image)
    print(message)
    if "Discard" in message:
        # Splitting on "Discard" results in an array like ['', '5 cards.\n\x0c'].
        # By getting the number this way, extra characters identified before
        # "Discard" will not break the result.
        return int(message.split("Discard ")[-1][:2])
    return 0

def look_for_mulligan_button() -> bool:
    '''Check if mulligan button is present on screen'''
    image = ImageGrab.grab(bbox=(946, 1142, 1151, 1197))
    image = ImageEnhance.Contrast(image).enhance(10)
    message = pytesseract.image_to_string(image)
    print(message)
    return "Mulligan" in message

def move_across_hand():
    mouse_position = (98, 1428)
    pyautogui.moveTo(mouse_position)
    id = 0
    handSize =  0
    while handSize < 5:
        mouse_position = (mouse_position[0] + 15, mouse_position[1])
        pyautogui.moveTo(mouse_position)
        log = get_newest_log()
        for line in log:
            if "objectId" in line:
                new_id = int(line.split('"objectId": ')[-1])
                if new_id != id:
                    print(f"found new id {new_id}")
                    id = new_id
                    handSize += 1
