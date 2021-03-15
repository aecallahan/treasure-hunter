'''
Transforms logs into corresponding mtg game data. Dispositions game_player's
directions to take corresponding action in game client.
'''
import os
import time

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

    # Append to log_parser_logs
    current_path = os.getcwd()
    file_writer = open(os.path.join(current_path, 'logs', 'log_parser_logs.log'), 'a')

    mull_message = identify_mulligan_message(log)
    if mull_message:
        game.hand = get_cards_in_hand_for_mulligan(mull_message)
        file_writer.write("deciding mulligan...\n")
        print("deciding mulligan...")
        game.decide_mulligan()
        if game.concede:
            file_writer.write("decided to concede\n")
            file_writer.close()
            print('decided to concede')
            mouse_controller.concede()
            return
        if game.mulligan:
            file_writer.write("decided to mulligan\n")
            print('decided to mulligan')
            game.mulligan_count += 1
            mouse_controller.mulligan()
        else:
            file_writer.write("decided to keep hand\n")
            print('decided to keep')
            mouse_controller.keepHand(game.mulligan_count, game)
        file_writer.close()
        return

    if is_player_step("Step_Draw", log):
        new_card = get_drawn_card_from_log(log)
        file_writer.write(f"drawing card {new_card}\n")
        print(f"drawing card {new_card}")
        game.hand.append(new_card)
    if is_player_phase("Phase_Main1", log, game):
        file_writer.write(f"entering main phase with hand {game.hand}\n")
        print(f"entering main phase with hand {game.hand}")
        game.decide_main_phase_actions()
        file_writer.write(f"playing cards at indices {game.indices_of_cards_to_play}\n")
        if game.concede:
            file_writer.close()
            mouse_controller.concede()
        time.sleep(1)
        # TODO: Crashes if beginning turn one on the play with just treasure hunt in hand.
        # See logs_on_the_play_one_card_in_hand for related logs.
        for index, action in game.indices_of_cards_to_play:
            play_card(index)
            if action == MYSTIC_SANCTUARY:
                mouse_controller.take_mystic_sanctuary_action()
            elif action == LONELY_SANDBAR:
                mouse_controller.playLonelySandbarSecondPrompt()
            elif action == "CYCLE":
                mouse_controller.cycle_lonely_sandbar()
            elif action == TREASURE_HUNT:
                time.sleep(4)
        # TODO: update hand immediately after playing treasure hunt and use drawn cards
        # to decide remainder of main phase actions
        if any(TREASURE_HUNT in sublist for sublist in game.indices_of_cards_to_play):
            file_writer.write("updating hand after playing treasure hunt\n")
            mouse_controller.close_revealed_cards()
            game.hand = update_hand_after_playing_treasure_hunt(game.hand)
            file_writer.write(f"hand after treasure hunt: {game.hand}\n")
            game.decide_discard()

        if game.tap_out:
            mouse_controller.tap_all_land()
        if game.indices_of_cards_to_discard:
            file_writer.write("waiting for discard message...\n")
            mouse_controller.wait_for_discard_message()
            discard_to_seven(game.indices_of_cards_to_discard)
            file_writer.write(f"hand after discard: {game.hand}\n")
        file_writer.close()

    # mouse_controller.click_submit()


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
    # TODO: this can throw a KeyError for 'gameObjects'
    try:
        for game_object in game_state["gameStateMessage"]["gameObjects"]:
            if game_object["instanceId"] in ids_of_cards_in_hand:
                player_hand.append(cardIdNames[game_object["name"]])
        return sorted(player_hand)
    except KeyError:
        print('key error while looking for hand during mulligan. conceding...')
        mouse_controller.concede()

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
            turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            print(f"drawing card on turn {turn}")
            return cardIdNames[client_message["gameStateMessage"]["gameObjects"][0]["name"]]
    return None

def get_object_id_from_newest_log() -> int:
    log = get_newest_log()
    for line in log:
        if "objectId" in line:
            try:
                return int(line.split('"objectId": ')[-1])
            except ValueError:
                try:
                    return int(line.split('objectId": ')[-1])
                except ValueError:
                    return None


def update_hand_after_playing_treasure_hunt(hand: list) -> list:
    '''Read through hand and append cards drawn from treasure hunt'''
    print("updating hand after playing treasure hunt")
    mouse_position = None
    seen_entire_hand = False
    object_id = 0
    num_of_cards_identified = 0
    # new_hand = []
    iterations_since_new_card_seen = 0
    while not seen_entire_hand:
        if mouse_position:
            mouse_position = mouse_controller.move_across_hand(mouse_position)
        else:
            mouse_position = mouse_controller.move_across_hand()
        new_object_id = get_object_id_from_newest_log()
        if new_object_id is not None and new_object_id != object_id:
            object_id = new_object_id
            num_of_cards_identified += 1
            iterations_since_new_card_seen = 0
            if num_of_cards_identified > len(hand):
                hand.append(mouse_controller.read_card_name_at_location(mouse_position))
            # new_hand.append(mouse_controller.read_card_name_at_location(mouse_position))
        else:
            iterations_since_new_card_seen += 1
            if num_of_cards_identified > 0 and iterations_since_new_card_seen > 20:
            # if len(new_hand) > len(hand) and iterations_since_new_card_seen > 20:
                seen_entire_hand = True
    # return new_hand
    return hand


def discard_to_seven(discard_indices: list):
    # import pdb; pdb.set_trace()
    print("indices of cards to discard:")
    print(discard_indices)
    object_id = 0
    card_index = -2
    mouse_position = None
    while discard_indices:
        if mouse_position:
            mouse_position = mouse_controller.move_across_hand(mouse_position)
        else:
            mouse_position = mouse_controller.move_across_hand()
        new_object_id = get_object_id_from_newest_log()
        if new_object_id != object_id:
            object_id = new_object_id
            card_index += 1
            if card_index == discard_indices[0]:
                mouse_controller.select_card_for_discard(mouse_position)
                discard_indices.pop(0)
    mouse_controller.click_submit()


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
