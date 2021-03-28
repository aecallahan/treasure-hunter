'''
Handles all mouse actions requested by game player
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

PLAY_BUTTON_POSITION = (2332, 1348)
NEXT_BUTTON_POSITION = (2367, 1266)

HAND_START_POSITION = (180, 1428)
HAND_START_POSITION_FAST = (380, 1428)

CENTER_OF_SCREEN = (1280, 720)

DECK_POSITION = (300, 1301)
# DECK_POSITION = CENTER_OF_SCREEN

LAND_START_POSITION = (400, 1040)

LAND_END_POSITION = (1000, 1040)

def read_card_name_at_location(mouse_position) -> str:
    subtractXStart = 150
    addXEnd = 150
    card_name = read_message_from_screen((mouse_position[0] - subtractXStart, \
        874, mouse_position[0] + addXEnd, 910))
    print(card_name)
    if "Lonely" in card_name or "Sandbar" in card_name:
        return LONELY_SANDBAR
    if "Mystic" in card_name or "Sanctuary" in card_name:
        return MYSTIC_SANCTUARY
    if "Thassa" in card_name or "Oracle" in card_name:
        return THASSAS_ORACLE
    if "easure" in card_name or "Hunt" in card_name:
        return TREASURE_HUNT
    return BASIC_ISLAND


def concede():
    '''Concedes the current game'''
    print("conceding")
    pyautogui.click(x=2515, y=45)
    pyautogui.moveTo(x=1280, y=854, duration=1)
    pyautogui.mouseDown(x=1280, y=854)
    time.sleep(0.25)
    pyautogui.mouseUp()

def wait_for_mulligan_priority():
    waiting_for_priority = True
    while waiting_for_priority:
        waiting_for_priority = not look_for_mulligan_button()

def wait_for_main_phase_priority():
    '''Wait until player has priority in main phase 1'''
    timeout = time.time() + 30
    while True:
        if time.time() > timeout:
            return
        if look_for_next_button():
            return
        if look_for_end_turn_button():
            return
        if look_for_next_button():
            return

def wait_for_resolve_priority():
    '''Wait until Resolve button appears on screen'''
    # Timeout after 30 seconds
    timeout = time.time() + 30
    while True:
        if time.time() > timeout:
            return
        if look_for_resolve_button():
            return
        if look_for_pass_button():
            return
        if look_for_next_button():
            return
        if look_for_my_turn_button():
            return

def wait_for_priority_after_casting_treasure_hunt():
    '''Wait for discard message or next button'''
    timeout = time.time() + 30
    while True:
        if time.time() > timeout:
            return
        if look_for_next_button():
            return
        if look_for_end_turn_button():
            return
        if look_for_discard_message():
            return


def wait_for_discard_message() -> str:
    '''Wait until player sees discard message on screen'''
    waiting_for_discard = True
    while waiting_for_discard:
        waiting_for_discard = not look_for_discard_message()

def playLonelySandbarSecondPrompt():
    time.sleep(0.5)
    pyautogui.click(x=951, y=652)
    pyautogui.moveTo(DECK_POSITION)

def cycle_lonely_sandbar():
    '''Select the 'cycle' option in lonely sandbar's second prompt'''
    time.sleep(0.5)
    pyautogui.click(x=1603, y=620)
    pyautogui.moveTo(DECK_POSITION)
    time.sleep(2)

def mousePickCardsAfterMulligan(mullCount: int):
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

    for _ in range(mullCount):
        position = positions.pop(0)
        pyautogui.moveTo(position, duration=0.2)
        pyautogui.dragTo(BOTTOM_OF_LIBRARY_POS, duration=0.5)

    time.sleep(0.1)
    pyautogui.click(x=1286, y=1158)
    pyautogui.moveTo(DECK_POSITION)

def mulligan():
    wait_for_mulligan_priority()
    print("mulligan button identified, clicking it now")
    pyautogui.click(x=1055, y=1166)
    pyautogui.moveTo(DECK_POSITION)

def keepHand(mullCount: int):
    wait_for_mulligan_priority()
    pyautogui.click(x=1518, y=1166)
    mousePickCardsAfterMulligan(mullCount)

def play_card():
    # Do not play card until p1 has priority
    wait_for_main_phase_priority()
    pyautogui.dragTo(CENTER_OF_SCREEN, duration=0.3)
    pyautogui.moveTo(DECK_POSITION)

def pass_priority():
    wait_for_resolve_priority()
    click_submit()

def look_for_next_button() -> bool:
    message = read_message_from_screen((2313, 1242, 2426, 1289))
    print(message)
    return "Next" in message

def look_for_pass_button() -> bool:
    message = read_message_from_screen((2313, 1242, 2426, 1289))
    print(message)
    return "Pass" in message

def look_for_end_turn_button() -> bool:
    message = read_message_from_screen((2250, 1242, 2500, 1289))
    print(message)
    # Don't read 'Opponent's Turn'
    if "pponen" in message:
        return False
    return "End" in message or "Turn" in message

def look_for_resolve_button() -> bool:
    message = read_message_from_screen((2250, 1242, 2500, 1289))
    print(message)
    return "esolve" in message

def look_for_my_turn_button() -> bool:
    message = read_message_from_screen((2250, 1242, 2500, 1289))
    print(message)
    # Don't read 'Opponent's Turn'
    if "pponen" in message:
        return False
    return "My" in message or "Turn" in message

def look_for_discard_message() -> bool:
    message = read_message_from_screen((1099, 577, 1430, 635))
    return "Discard" in message

def look_for_mulligan_button() -> bool:
    '''Check if mulligan button is present on screen'''
    message = read_message_from_screen((946, 1142, 1151, 1197))
    print(message)
    return "Mulligan" in message

def move_across_hand(mouse_position=HAND_START_POSITION) -> tuple:
    if mouse_position == None:
        mouse_position = HAND_START_POSITION
    pyautogui.moveTo(mouse_position)
    return (mouse_position[0] + 20, mouse_position[1])

def move_across_hand_fast(mouse_position=HAND_START_POSITION_FAST) -> tuple:
    if mouse_position == None:
        mouse_position = HAND_START_POSITION_FAST
    pyautogui.moveTo(mouse_position)
    return (mouse_position[0] + 80, mouse_position[1])

def tap_all_land():
    '''Incrementally move mouse across lands to tap them all.'''
    time.sleep(1)
    close_revealed_cards()
    mouse_position=LAND_START_POSITION
    pyautogui.moveTo(mouse_position)
    while mouse_position[0] < LAND_END_POSITION[0]:
        pyautogui.click(mouse_position)
        mouse_position = (mouse_position[0] + 20, mouse_position[1])
    click_submit()

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
    '''Clicks submit/next button'''
    pyautogui.click(NEXT_BUTTON_POSITION)
    pyautogui.moveTo(DECK_POSITION)

def click_play():
    '''Clicks the play button'''
    pyautogui.click(PLAY_BUTTON_POSITION)

def close_revealed_cards():
    '''Clicks 'x' button to close popup revealing cards drawn with Treasure Hunt'''
    pyautogui.click(x=470, y=854)
    # pyautogui.moveTo(DECK_POSITION)

def take_mystic_sanctuary_action():
    print("taking mystic sanctuary action")
    time.sleep(1)
    pyautogui.click(x=1794, y=672)
    time.sleep(1.5)
    pyautogui.click(x=2370, y=1269)
    pyautogui.moveTo(DECK_POSITION)

def start_new_game():
    '''Click through end of game messages and start new one'''
    for i in range(7):
        time.sleep(5)
        click_play()
