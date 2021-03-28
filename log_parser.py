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
    if is_game_over(log):
        print_and_write_log("Finished game, starting new one")
        game.reset_game()
        mouse_controller.start_new_game()
        return

    if "greToClientEvent" not in log:
        return

    mull_message = identify_mulligan_message(log)
    if mull_message:
        game.hand = get_cards_in_hand_for_mulligan(mull_message)
        print_and_write_log("deciding mulligan...")
        game.decide_mulligan()
        if game.concede:
            print_and_write_log("decided to concede")
            mouse_controller.concede()
            return
        if game.mulligan:
            print_and_write_log("decided to mulligan")
            game.mulligan_count += 1
            mouse_controller.mulligan()
        else:
            print_and_write_log("decided to keep hand")
            game.hand = game.hand[game.mulligan_count:]
            mouse_controller.keepHand(game.mulligan_count)
        return

    if is_player_step("Step_Draw", log):
        new_card = get_drawn_card_from_log(log)
        game.played_cards_for_turn = False
        print_and_write_log(f"drawing card {new_card}")
        if new_card:
            game.hand.append(new_card)
    if not game.played_cards_for_turn and is_player_phase("Phase_Main1", log, game):
        print_and_write_log(f"entering main phase with hand {game.hand}")
        game.decide_main_phase_actions()
        print_and_write_log(f"playing cards at indices {game.indices_of_cards_to_play}")
        if game.concede:
            mouse_controller.concede()
        time.sleep(1.5)
        for i in range(len(game.indices_of_cards_to_play)):
            index, action = game.indices_of_cards_to_play[i]
            print(f"playing card at position {index}")
            play_card(index, len(game.hand))
            game.hand.pop(index)
            # for remaining indices of cards to play, decrement to account for pop
            for j in range(i + 1, len(game.indices_of_cards_to_play)):
                if game.indices_of_cards_to_play[j][0] > index:
                    game.indices_of_cards_to_play[j][0] -= 1
            if action == MYSTIC_SANCTUARY:
                mouse_controller.take_mystic_sanctuary_action()
            elif action == LONELY_SANDBAR:
                mouse_controller.playLonelySandbarSecondPrompt()
            elif action == "CYCLE":
                mouse_controller.cycle_lonely_sandbar()
                game.hand.append(TREASURE_HUNT)
            elif action == TREASURE_HUNT:
                mouse_controller.wait_for_priority_after_casting_treasure_hunt()
                mouse_controller.close_revealed_cards()
                game.hand = update_hand_after_playing_treasure_hunt(game.hand)
                print_and_write_log(f"hand after treasure hunt: {game.hand}")

        if len(game.indices_of_cards_to_play) <= 1:
            time.sleep(1)
            mouse_controller.click_submit()

        if len(game.hand) > 7:
            game.decide_discard()

        if game.indices_of_cards_to_discard:
            if cycling_available(log):
                print_and_write_log("identified cycling is available, " \
                    + "clicking next before discarding")
                time.sleep(1)
                mouse_controller.click_submit()
                time.sleep(1)
                mouse_controller.click_submit()
            discard_to_seven(game.indices_of_cards_to_discard)
            print_and_write_log(f"hand after discard: {game.hand}")
    elif cycling_available(log):
        if current_player_turn(log) == 1:
            print_and_write_log("identified cycling is available, clicking next")
            time.sleep(1)
            mouse_controller.click_submit()
        else:
            # TODO: seems this identifies priority in opponent's upkeep even though there's no prompt
            # This gets the logs out of sync
            print_and_write_log("identified cycling is available on opponent's turn")
            mouse_controller.pass_priority()


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
    hand_zone1 = game_state["gameStateMessage"]["zones"][0]
    ids_of_cards_in_hand1 = set(hand_zone1["objectInstanceIds"])
    ids_of_cards_in_hand2 = set()
    if len(game_state["gameStateMessage"]["zones"]) > 2:
        hand_zone2 = game_state["gameStateMessage"]["zones"][2]
        ids_of_cards_in_hand2 = set(hand_zone2["objectInstanceIds"])
    player_hand = []

    for game_object in game_state["gameStateMessage"].get("gameObjects", []):
        if game_object["instanceId"] in ids_of_cards_in_hand1.union(ids_of_cards_in_hand2):
            player_hand.append(cardIdNames[game_object["name"]])

    print_and_write_log(f"identified hand of {player_hand}")
    return sorted(player_hand)


def is_game_over(log: dict) -> bool:
    return "finalMatchResult" in log.get( \
        "matchGameRoomStateChangedEvent", {}).get("gameRoomInfo", {})

def is_player_step(step: str, log: dict) -> bool:
    '''Checks current log to see if it is the requested step'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("step") == step \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1:
            return True
    return False

def is_player_phase(phase: str, log: dict, game: GameStateObject) -> bool:
    '''Checks current log to see if it is the requested phase'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("phase") == phase \
          and client_message["gameStateMessage"]["turnInfo"]["activePlayer"] == 1 \
          and client_message["gameStateMessage"]["turnInfo"]["turnNumber"] > game.turn:
            turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            print_and_write_log(f"main phase identified on turn {turn}")
            game.turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            return True
    return False

def current_player_turn(log: dict) -> int:
    '''Checks current log to see who's turn it is'''
    for client_message in log["greToClientEvent"]["greToClientMessages"]:
        if client_message.get("gameStateMessage", {}).get("turnInfo", {}).get("activePlayer"):
            return client_message["gameStateMessage"]["turnInfo"]["activePlayer"]


def get_drawn_card_from_log(log: dict):
    '''Checks log for card drawn and updates game state accordingly'''
    for client_message in reversed(log["greToClientEvent"]["greToClientMessages"]):
        if "gameObjects" in client_message.get("gameStateMessage", {}) and \
          client_message["gameStateMessage"]["gameObjects"][0]["ownerSeatId"] == 1:
            turn = client_message["gameStateMessage"]["turnInfo"]["turnNumber"]
            print_and_write_log(f"drawing card on turn {turn}")
            try:
                return cardIdNames[client_message["gameStateMessage"]["gameObjects"][0]["name"]]
            except KeyError:
                continue
    return None

def cycling_available(log: dict) -> bool:
    '''Read log and check if user has priority for cycling'''
    if not log.get("greToClientEvent", {}).get("greToClientMessages", {}):
        return False
    if "actionsAvailableReq" not in log["greToClientEvent"]["greToClientMessages"][-1]:
        return False
    # TODO: this if doesn't give up priority in opponent's main phase
    # Need to find a way to give up priority in upkeep instead
    # if log["greToClientEvent"]["greToClientMessages"][0].get("gameStateMessage", \
    #   {}).get("turnInfo", {}).get("phase") == "Phase_Main1":
    #     return False
    actions = log["greToClientEvent"]["greToClientMessages"][-1]["actionsAvailableReq"]["actions"]
    for action in actions:
        if action["actionType"] == "ActionType_Activate" and action["shouldStop"]:
            return True
    return False

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
    print_and_write_log("updating hand after playing treasure hunt")
    mouse_position = None
    seen_entire_hand = False
    object_id = 0
    num_of_cards_identified = 0
    iterations_since_new_card_seen = 0
    while not seen_entire_hand:
        mouse_position = mouse_controller.move_across_hand(mouse_position)
        new_object_id = get_object_id_from_newest_log()
        if new_object_id is not None and new_object_id != object_id:
            object_id = new_object_id
            num_of_cards_identified += 1
            iterations_since_new_card_seen = 0
            if num_of_cards_identified > len(hand):
                hand.append(mouse_controller.read_card_name_at_location(mouse_position))
        else:
            iterations_since_new_card_seen += 1
            if num_of_cards_identified > 0 and iterations_since_new_card_seen > 20:
                seen_entire_hand = True
    return hand


def discard_to_seven(discard_indices: list):
    print_and_write_log("indices of cards to discard:")
    print_and_write_log(discard_indices)
    object_id = 0
    card_index = -2
    mouse_position = None
    while discard_indices:
        mouse_position = mouse_controller.move_across_hand(mouse_position)
        new_object_id = get_object_id_from_newest_log()
        if new_object_id != object_id:
            object_id = new_object_id
            card_index += 1
            if card_index == discard_indices[0]:
                mouse_controller.select_card_for_discard(mouse_position)
                discard_indices.pop(0)
    mouse_controller.click_submit()


def play_card(position: int, hand_size: int):
    print_and_write_log(f"playing card at position {position}")
    current_card = -1
    object_id = 0
    mouse_position = move_across_hand(None, hand_size)
    while current_card < position:
        mouse_position = move_across_hand(mouse_position, hand_size)
        new_object_id = get_object_id_from_newest_log()
        if new_object_id is not None and new_object_id != object_id:
            object_id = new_object_id
            current_card += 1
    mouse_controller.play_card()


def print_and_write_log(message: str):
    '''Print to console and write to log'''
    current_path = os.getcwd()
    file_writer = open(os.path.join(current_path, 'logs', 'log_parser_logs.log'), 'a')
    file_writer.write(f"{message}\n")
    print(message)
    file_writer.close()

def move_across_hand(mouse_position: tuple, hand_size: int) -> tuple:
    '''Decide whether to invoke fast or slow function to move across hand'''
    if hand_size > 8:
        return mouse_controller.move_across_hand(mouse_position)
    return mouse_controller.move_across_hand_fast(mouse_position)
