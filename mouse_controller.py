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

# 2560, 1440
screenWidth, screenHeight = pyautogui.size()

PLAY_BUTTON_POSITION = (0.911 * screenWidth, 0.936 * screenHeight)
# PLAY_BUTTON_POSITION = (2332, 1348)
NEXT_BUTTON_POSITION = (0.925 * screenWidth, 0.879 * screenHeight)
# NEXT_BUTTON_POSITION = (2367, 1266)

HAND_START_POSITION = (0.07 * screenWidth, 0.992 * screenHeight)
HAND_START_POSITION_FAST = (0.148 * screenWidth, 0.992 * screenHeight)
# HAND_START_POSITION = (180, 1428)
# HAND_START_POSITION_FAST = (380, 1428)

CENTER_OF_SCREEN = (0.5 * screenWidth, 0.5 * screenHeight)

# DECK_POSITION = (300, 1301)
DECK_POSITION = (0.117 * screenWidth, 0.903 * screenHeight)

# LAND_START_POSITION = (400, 1040)
LAND_START_POSITION = (400, 1040)

# LAND_END_POSITION = (1000, 1040)
LAND_END_POSITION = (0.391 * screenWidth, 0.722 * screenHeight)

def read_card_name_at_location(mouse_position) -> str:
    # subtractXStart = 150
    # addXEnd = 150
    subtract_x_start = 0.0586 * screenWidth
    add_x_end = 0.0586 * screenWidth
    # card_name = read_message_from_screen((mouse_position[0] - subtract_x_start, \
    #     874, mouse_position[0] + add_x_end, 910))
    card_name = read_message_from_screen((mouse_position[0] - subtract_x_start, \
        0.607 * screenHeight, mouse_position[0] + add_x_end, 0.632 * screenHeight))
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
    # pyautogui.click(x=2515, y=45)
    # pyautogui.moveTo(x=1280, y=854, duration=1)
    # pyautogui.mouseDown(x=1280, y=854)
    pyautogui.click(x=0.982 * screenWidth, y=0.0313 * screenHeight)
    pyautogui.moveTo(x=0.5 * screenWidth, y=0.593 * screenHeight, duration=1)
    pyautogui.mouseDown(x=0.5 * screenWidth, y=0.593 * screenHeight)
    time.sleep(0.25)
    pyautogui.mouseUp()

def wait_for_mulligan_priority():
    waiting_for_priority = True
    while waiting_for_priority:
        waiting_for_priority = not look_for_mulligan_button()

def wait_for_main_phase_priority():
    '''Wait until player has priority in main phase 1'''
    # timeout = time.time() + 30
    while True:
        # if time.time() > timeout:
        #     return
        if look_for_next_button():
            return
        if look_for_end_turn_button():
            return
        if look_for_next_button():
            return

def wait_for_resolve_priority():
    '''Wait until Resolve button appears on screen'''
    # Timeout after 30 seconds
    # timeout = time.time() + 30
    while True:
        # if time.time() > timeout:
        #     return
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
    # timeout = time.time() + 30
    while True:
        # if time.time() > timeout:
        #     return
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
    pyautogui.click(x=0.371 * screenWidth, y=0.453 * screenHeight)
    pyautogui.moveTo(DECK_POSITION)

def cycle_lonely_sandbar():
    '''Select the 'cycle' option in lonely sandbar's second prompt'''
    time.sleep(0.5)
    pyautogui.click(x=1603, y=620)
    pyautogui.moveTo(DECK_POSITION)
    time.sleep(2)

def mousePickCardsAfterMulligan(mullCount: int):
    bottom_of_library_pos = (0.135 * screenWidth, 0.521 * screenHeight)
    seventh_card_pos = (0.468 * screenWidth, 0.455 * screenHeight)
    sixth_card_pos = (0.484 * screenWidth, 0.449 * screenHeight)
    fifth_card_pos = (0.531 * screenWidth, 0.503 * screenHeight)
    fourth_card_pos = (0.566 * screenWidth, 0.474 * screenHeight)
    third_card_pos = (0.609 * screenWidth, 0.481 * screenHeight)
    second_card_pos = (0.633 * screenWidth, 0.481 * screenHeight)
    positions = [
        seventh_card_pos,
        sixth_card_pos,
        fifth_card_pos,
        fourth_card_pos,
        third_card_pos,
        second_card_pos,
    ]

    for _ in range(mullCount):
        position = positions.pop(0)
        pyautogui.moveTo(position, duration=0.2)
        pyautogui.dragTo(bottom_of_library_pos, duration=0.5)

    time.sleep(0.1)
    pyautogui.click(x=0.502 * screenWidth, y=0.804 * screenHeight)
    pyautogui.moveTo(DECK_POSITION)

def mulligan():
    print("waiting for mulligan priority...")
    wait_for_mulligan_priority()
    print("mulligan button identified, clicking it now")
    pyautogui.click(x=0.412 * screenWidth, y=0.81 * screenHeight)
    pyautogui.moveTo(DECK_POSITION)

def keepHand(mullCount: int):
    print("waiting for mulligan priority...")
    wait_for_mulligan_priority()
    pyautogui.click(x=0.593 * screenWidth, y=0.81 * screenHeight)
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
    message = read_message_from_screen((0.904 * screenWidth, 0.863 * screenHeight,
        0.948 * screenWidth, 0.895 * screenHeight))
    print(message)
    return "Next" in message

def look_for_pass_button() -> bool:
    message = read_message_from_screen((0.904 * screenWidth, 0.863 * screenHeight,
        0.948 * screenWidth, 0.895 * screenHeight))
    print(message)
    return "Pass" in message

def look_for_end_turn_button() -> bool:
    message = read_message_from_screen((0.879 * screenWidth, 0.863 * screenHeight,
        0.977 * screenWidth, 0.895 * screenHeight))
    print(message)
    # Don't read 'Opponent's Turn'
    if "pponen" in message:
        return False
    return "End" in message or "Turn" in message

def look_for_resolve_button() -> bool:
    message = read_message_from_screen((0.879 * screenWidth, 0.863 * screenHeight,
        0.977 * screenWidth, 0.895 * screenHeight))
    print(message)
    return "esolve" in message

def look_for_my_turn_button() -> bool:
    message = read_message_from_screen((0.879 * screenWidth, 0.863 * screenHeight,
        0.977 * screenWidth, 0.895 * screenHeight))
    print(message)
    # Don't read 'Opponent's Turn'
    if "pponen" in message:
        return False
    return "My" in message or "Turn" in message

def look_for_discard_message() -> bool:
    message = read_message_from_screen((0.430 * screenWidth, 0.401 * screenHeight,
        0.559 * screenWidth, 0.441 * screenHeight))
    return "Discard" in message

def look_for_mulligan_button() -> bool:
    '''Check if mulligan button is present on screen'''
    message = read_message_from_screen((0.37 * screenWidth, 0.793 * screenHeight,
        0.45 * screenWidth, 0.831 * screenHeight))
    print(message)
    return "Mulligan" in message

def move_across_hand(mouse_position=HAND_START_POSITION) -> tuple:
    if mouse_position is None:
        mouse_position = HAND_START_POSITION
    pyautogui.moveTo(mouse_position)
    return (mouse_position[0] + (0.007 * screenWidth), mouse_position[1])

def move_across_hand_fast(mouse_position=HAND_START_POSITION_FAST) -> tuple:
    if mouse_position is None:
        mouse_position = HAND_START_POSITION_FAST
    pyautogui.moveTo(mouse_position)
    return (mouse_position[0] + (0.031 * screenWidth), mouse_position[1])

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
    pyautogui.click(x=0.184 * screenWidth, y=0.593 * screenHeight)

def take_mystic_sanctuary_action():
    print("taking mystic sanctuary action")
    time.sleep(1)
    pyautogui.click(x=0.701 * screenWidth, y=0.467 * screenHeight)
    time.sleep(2.5)
    pyautogui.click(x=0.926 * screenWidth, y=0.881 * screenHeight)
    pyautogui.moveTo(DECK_POSITION)

def tap_all_lands():
    '''Double tap q to tap all lands'''
    pyautogui.keyDown("q")
    time.sleep(0.1)
    pyautogui.keyUp("q")
    time.sleep(0.1)
    pyautogui.keyDown("q")
    time.sleep(0.1)
    pyautogui.keyUp("q")

def start_new_game():
    '''Click through end of game messages and start new one'''
    for i in range(6):
        time.sleep(7)
        pyautogui.mouseDown(PLAY_BUTTON_POSITION)
        time.sleep(0.25)
        pyautogui.mouseUp()
        click_play()
    print("finished pressing buttons to play again")
