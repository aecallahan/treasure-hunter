'''
This module handles logic of playing games
'''
import time

import pytesseract

import mouse

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

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


class GameStateObject:
    '''Represents the state of a mtg game'''
    def __init__(self):
        self.hand = []
        self.yard = []
        self.lands = 0
        self.tapped_lands = 0
        self.land_for_turn = False

    def reset(self):
        '''Reset game state'''
        self.__init__()


def decide_mulligan(game_state: dict, game: GameStateObject):
    '''Decides whether to keep hand or mulligan based on presence of Treasure Hunt'''
    player = game_state["gameStateMessage"]["players"][0]
    mulligan_count = player.get("mulligan_count", 0)
    current_hand_size = player["maxHandSize"] - mulligan_count
    print(f"currently mulliganing to {current_hand_size} cards")

    hand_zone = game_state["gameStateMessage"]["zones"][0]
    # Defensive checks because not sure first zone is always p1's hand
    if hand_zone["type"] != "ZoneType_Hand":
        print("Error: hand_zone was not first zone")
    if hand_zone["visibility"] != "Visibility_Private":
        print("Error: hand_zone was not Visibility_Private")
    if hand_zone["ownerSeatId"] != 1:
        print("Error: hand_zone wasn't owned by player 1")

    ids_of_cards_in_hand = set(hand_zone["objectInstanceIds"])
    player_hand = []
    for game_object in game_state["gameStateMessage"]["gameObjects"]:
        if game_object["instanceId"] in ids_of_cards_in_hand:
            player_hand.append(cardIdNames[game_object["name"]])

    waiting_for_priority = True
    while waiting_for_priority:
        waiting_for_priority = not mouse.look_for_mulligan_button()

    if TREASURE_HUNT not in player_hand:
        if current_hand_size == 1:
            mouse.concede()
        else:
            mouse.mulligan(mulligan_count)
    else:
        # Sorting alphabetically puts hand in same order as client, left to right
        player_hand.sort()
        game.hand = player_hand
        print(f"keeping hand: {game.hand}")
        mouse.keepHand(mulligan_count, game)


def is_player_step(step: str, log: dict) -> bool:
    '''Checks current log to see if it is the requested step'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("step") == step \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            return True
    return False

def is_player_phase(phase: str, log: dict) -> bool:
    '''Checks current log to see if it is the requested phase'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("phase") == phase \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            return True
    return False

def update_hand_with_draw(log: dict, game: GameStateObject):
    '''Checks log for card drawn and updates game state accordingly'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if "gameObjects" in client_message.get("gameStateMessage", {}) and \
          client_message["gameStateMessage"]["gameObjects"][0]["ownerSeatId"] == 1:
            game.hand.append( \
                cardIdNames[client_message["gameStateMessage"]["gameObjects"][0]["name"]])
            print(f"hand after draw: {game.hand}")


def identify_mulligan_message(log: dict) -> dict:
    '''Looks for a portion of the log specific to mulliganing and returns it if found'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message["type"] != "GREMessageType_GameStateMessage":
            continue
        if "gameStateMessage" in client_message and \
          "players" in client_message["gameStateMessage"] and \
          client_message["gameStateMessage"]["players"][0].get("pendingMessageType") \
          == "ClientMessageType_MulliganResp":
            return client_message
    return None

def play_island(game: GameStateObject):
    '''Plays a basic island'''
    if BASIC_ISLAND not in game.hand:
        return
    print("playing island")
    print(f"hand before playing: {game.hand}")
    index = game.hand.index(BASIC_ISLAND)
    print(f"playing card at position {index}")
    mouse.playCard(index, game)
    game.land_for_turn = True
    game.lands += 1

def play_treasure_hunt(game: GameStateObject):
    '''Casts Treasure Hunt'''
    print("playing treasure hunt")
    print(f"hand before playing: {game.hand}")
    index = game.hand.index(TREASURE_HUNT)
    print(f"playing card at position {index}")
    mouse.playCard(index, game)
    game.tapped_lands += 2
    game.yard.append(TREASURE_HUNT)


def take_game_action(log: dict, game: GameStateObject):
    '''Reads latest log and decides what to do'''
    if "greToClientEvent" not in log:
        return
    mull_message = identify_mulligan_message(log)
    if mull_message:
        decide_mulligan(mull_message, game)
    else:
        if is_player_step("Step_Draw", log):
            print("drawing card")
            update_hand_with_draw(log, game)
            game.land_for_turn = False
            game.tapped_lands = 0
        # TODO: doesn't work if mulliganed to 1 card and it's treasure hunt
        if is_player_phase("Phase_Main1", log):
            if not game.land_for_turn:
                play_island(game)
            if TREASURE_HUNT in game.hand and game.lands - game.tapped_lands >= 2:
                play_treasure_hunt(game)
                thirty_seconds_from_now = time.time() + 30
                # TODO: this doesn't work if opponent has priority during turn and does something
                while time.time() < thirty_seconds_from_now:
                    discard_number = mouse.read_number_of_cards_to_discard()
                    if discard_number > 0:
                        mouse.discardToSeven(discard_number, game)
                        return
