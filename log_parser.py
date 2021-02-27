'''
Transforms logs into corresponding mtg game data. Dispositions game_player's
directions to take corresponding action in game client.
'''
import time

from game_player import cardIdNames, GameStateObject
import mouse_controller

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
        for i, index in enumerate(cards_to_play):
            # Janky line to get rid of once implementing new method of finding correct card
            hand_size = len(game.hand) + len(cards_to_play) - i
            mouse_controller.playCard(index, hand_size)
        # TODO: maybe see if there's a way to do discard from a separate log rather than this one
        if len(cards_to_play) > 1:
            thirty_seconds_from_now = time.time() + 30
            # TODO: this doesn't work if opponent has priority during turn and does something
            while time.time() < thirty_seconds_from_now:
                discard_number = mouse_controller.read_number_of_cards_to_discard()
                if discard_number > 0:
                    mouse_controller.discardToSeven(discard_number, game)
                    return


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
