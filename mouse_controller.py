'''
Module handles all mouse actions requested by game player
'''
import time
import pyautogui
from PIL import ImageEnhance, ImageGrab
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"

NEXT_BUTTON_POSITION = (2367, 1266)

MOVE_ACROSS_HAND_STARTING_POSITION = (180, 1428)

DECK_POSITION = (300, 1301)

def read_card_name_during_discard(mouse_position) -> str:
    subtractXStart = 150
    addXEnd = 150
    card_name = read_message_from_screen((mouse_position[0] - subtractXStart, \
        874, mouse_position[0] + addXEnd, 910))
    print(card_name)
    if "Mystic" in card_name or "Sanctuary" in card_name:
        return MYSTIC_SANCTUARY
    if "Treasure" in card_name or "Hunt" in card_name:
        return TREASURE_HUNT
    if "Thassa" in card_name or "Oracle" in card_name:
        return THASSAS_ORACLE
    return BASIC_ISLAND


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

def wait_for_discard_message():
    waiting_for_discard = True
    while waiting_for_discard:
        waiting_for_discard = not look_for_discard_message() or lookForNextButton()

def playLonelySandbarSecondPrompt():
    time.sleep(0.5)
    pyautogui.click(x=951, y=652)
    pyautogui.moveTo(DECK_POSITION)

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
    pyautogui.moveTo(DECK_POSITION)

def mulligan():
    wait_for_mulligan_priority()
    pyautogui.click(x=1055, y=1166)
    pyautogui.moveTo(x=286, y=1286)

def keepHand(mullCount: int, game):
    wait_for_mulligan_priority()
    pyautogui.click(x=1518, y=1166)
    mousePickCardsAfterMulligan(mullCount, game)

def play_card():
    # Do not play card until p1 has priority
    wait_for_main_phase_priority()
    pyautogui.dragTo((1280, 720), duration=0.3)
    pyautogui.moveTo(DECK_POSITION)

def lookForNextButton() -> bool:
    message = read_message_from_screen((2313, 1242, 2426, 1289))
    print(message)
    return "Next" in message

def look_for_discard_message() -> bool:
    message = read_message_from_screen((1099, 577, 1430, 635))
    return "Discard" in message

def read_number_of_cards_to_discard() -> int:
    '''Read message in center of screen instructing player to discard to hand size'''
    # TODO: doesn't handle message "Discard a card"
    message = read_message_from_screen((1099, 577, 1430, 635))
    print(message)
    if "Discard" in message:
        # Splitting on "Discard" results in an array like ['', '5 cards.\n\x0c'].
        # By getting the number this way, extra characters identified before
        # "Discard" will not break the result.
        try:
            return int(message.split("Discard ")[-1][:2])
        except ValueError:
            # '11' read as 'll'
            if message.split("Discard ")[-1][:2] == "ll":
                return 11
            return 1
    return 0

def look_for_mulligan_button() -> bool:
    '''Check if mulligan button is present on screen'''
    message = read_message_from_screen((946, 1142, 1151, 1197))
    print(message)
    return "Mulligan" in message

def move_across_hand(mouse_position=MOVE_ACROSS_HAND_STARTING_POSITION) -> tuple:
    pyautogui.moveTo(mouse_position)
    return (mouse_position[0] + 20, mouse_position[1])

def select_card_for_discard(mouse_position):
    pyautogui.click(mouse_position)

def read_message_from_screen(bbox: tuple) -> str:
    image = ImageGrab.grab(bbox)
    image = ImageEnhance.Contrast(image).enhance(10)
    index = 0
    image.save(f'viewed_image_{index}.png')
    # TODO: set tesseract config to only read alphanumeric characters
    return pytesseract.image_to_string(image)

def click_submit():
    '''Clicks submit button'''
    pyautogui.click(NEXT_BUTTON_POSITION)
    pyautogui.moveTo(DECK_POSITION)

def close_revealed_cards():
    '''Clicks 'x' button to close popup revealing cards drawn with Treasure Hunt'''
    pyautogui.click(x=470, y=854)
    pyautogui.moveTo(DECK_POSITION)

def take_mystic_sanctuary_action():
    print("taking mystic sanctuary action")
    time.sleep(1)
    pyautogui.click(x=1794, y=672)
    time.sleep(1)
    pyautogui.click(x=2370, y=1269)
    pyautogui.moveTo(DECK_POSITION)
