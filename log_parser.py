'''
Transforms logs into corresponding mtg game data. Dispositions game_player's
directions to take corresponding action in game client.
'''
from game_player import cardIdNames, GameStateObject
from log_crawler import get_newest_log
import mouse_controller

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"

def parse_log(log: dict, game: GameStateObject):
    '''Read latest log and decide what to do'''
    if "greToClientEvent" not in log:
        return
    mull_message = identify_mulligan_message(log)
    if mull_message:
        game.hand = get_cards_in_hand_for_mulligan(mull_message)
        game.decide_mulligan()
        if game.concede:
            mouse_controller.concede()
            return
        if game.mulligan:
            game.mulligan_count += 1
            mouse_controller.mulligan()
        else:
            mouse_controller.keepHand(game.mulligan_count, game)
        return

    if is_player_step("Step_Draw", log):
        new_card = get_drawn_card_from_log(log)
        print(f"drawing card {new_card}")
        game.hand.append(new_card)
    if is_player_phase("Phase_Main1", log, game):
        print(f"entering main phase with hand {game.hand}")
        # import pdb; pdb.set_trace()
        cards_to_play = game.main_phase_actions()
        print(f"playing cards at indices {cards_to_play}")
        for index in cards_to_play:
            play_card(index)
            if game.mystic_sanctuary_action:
                mouse_controller.take_mystic_sanctuary_action()
                game.mystic_sanctuary_action = False
        # TODO: maybe see if there's a way to do discard from a separate log rather than this one
        if game.will_discard:
            print("waiting for discard message...")
            mouse_controller.wait_for_discard_message()
            num_of_cards_to_discard = mouse_controller.read_number_of_cards_to_discard()
            if num_of_cards_to_discard > 0:
                mouse_controller.close_revealed_cards()
                # mouse_controller.discardToSeven(num_of_cards_to_discard, game)
                game.hand = discard_to_seven(num_of_cards_to_discard)
                return
    mouse_controller.click_submit()


def identify_mulligan_message(log: dict) -> dict:
    '''Look for a portion of the log specific to mulliganing and return it if found'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message["type"] != "GREMessageType_GameStateMessage":
            continue
        if "gameStateMessage" in client_message and \
          "players" in client_message["gameStateMessage"] and \
          client_message["gameStateMessage"]["players"][0].get("pendingMessageType") \
          == "ClientMessageType_MulliganResp":
            return client_message
    return None


def get_cards_in_hand_for_mulligan(game_state: dict) -> list:
    '''Parse log and populate game object with hand during mulligan decision.'''
    player = game_state["gameStateMessage"]["players"][0]
    mulligan_count = player.get("mulligan_count", 0)
    current_hand_size = player["maxHandSize"] - mulligan_count
    print(f"currently mulliganing to {current_hand_size} cards")
    hand_zone = game_state["gameStateMessage"]["zones"][0]

    ids_of_cards_in_hand = set(hand_zone["objectInstanceIds"])
    player_hand = []
    for game_object in game_state["gameStateMessage"]["gameObjects"]:
        if game_object["instanceId"] in ids_of_cards_in_hand:
            player_hand.append(cardIdNames[game_object["name"]])
    return sorted(player_hand)

def is_player_step(step: str, log: dict) -> bool:
    '''Checks current log to see if it is the requested step'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("step") == step \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            turn = client_message["gameStateMessage"]["turnInfo"]["activePlayer"]
            print(f"draw step identified on turn {turn}")
            return True
    return False

def is_player_phase(phase: str, log: dict, game: GameStateObject) -> bool:
    '''Checks current log to see if it is the requested phase'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("phase") == phase \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1 \
          and client_message["gameStateMessage"]["turnInfo"]["turnNumber"] > game.turn:
            turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            print(f"main phase identified on turn {turn}")
            game.turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            return True
    return False

def get_drawn_card_from_log(log: dict):
    '''Checks log for card drawn and updates game state accordingly'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if "gameObjects" in client_message.get("gameStateMessage", {}) and \
          client_message["gameStateMessage"]["gameObjects"][0]["ownerSeatId"] == 1:
            return cardIdNames[client_message["gameStateMessage"]["gameObjects"][0]["name"]]
    return None

def get_object_id_from_newest_log() -> int:
    log = get_newest_log()
    for line in log:
        if "objectId" in line:
            try:
                return int(line.split('"objectId": ')[-1])
            except ValueError:
                return int(line.split('objectId": ')[-1])

def discard_to_seven(num_of_cards_to_discard: int):
    new_hand = []
    object_id = 0
    num_of_cards_discarded = 0
    num_of_cards_identified = 0
    current_hand_size = num_of_cards_to_discard + 7
    mouse_position = None
    print(f"number of cards to discard: {num_of_cards_to_discard}")
    while num_of_cards_identified <= current_hand_size:
        print(f"number of cards discarded: {num_of_cards_discarded}")
        if mouse_position:
            mouse_position = mouse_controller.move_across_hand(mouse_position)
        else:
            mouse_position = mouse_controller.move_across_hand()
        new_object_id = get_object_id_from_newest_log()
        if new_object_id != object_id:
            object_id = new_object_id
            num_of_cards_identified += 1
            card_name = mouse_controller.read_card_name_during_discard(mouse_position)
            if num_of_cards_discarded <= num_of_cards_to_discard and card_name == BASIC_ISLAND:
                mouse_controller.select_card_for_discard(mouse_position)
                num_of_cards_discarded += 1
            else:
                new_hand.append(card_name)
    mouse_controller.click_submit()
    return new_hand

def play_card(position: int):
    print(f"playing card at position {position}")
    current_card = -1
    object_id = 0
    mouse_position = mouse_controller.move_across_hand()
    while current_card < position:
        mouse_position = mouse_controller.move_across_hand(mouse_position)
        new_object_id = get_object_id_from_newest_log()
        if new_object_id is not None and new_object_id != object_id:
            object_id = new_object_id
            current_card += 1
    mouse_controller.play_card()

