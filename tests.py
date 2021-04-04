'''unit tests'''
import json
import os
import time
import unittest
from unittest.mock import MagicMock, mock_open, patch

from executor import play_game
from game_player import GameStateObject
import log_crawler
import log_parser
import mouse_controller

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"


class TestGamePlayer(unittest.TestCase):
    '''Test cases for game_player.py'''

    def test_mulligan_if_no_treasure_hunt(self):
        '''
        Assert that game player decides to mulligan when presented with an opening hand
        missing Treasure Hunt
        '''
        game = GameStateObject()
        game.hand = [BASIC_ISLAND] * 7
        game.decide_mulligan()
        self.assertTrue(game.mulligan, "game player should've decided to mulligan")

    def test_no_mulligan_if_treasure_hunt(self):
        '''
        Assert that game player decides to keep an opening hand containing Treasure Hunt
        '''
        game = GameStateObject()
        game.hand = [BASIC_ISLAND] * 6 + [TREASURE_HUNT]
        game.decide_mulligan()
        self.assertFalse(game.mulligan, "game player should've decided to keep")

    def test_treasure_hunt_on_two_after_mystic_sanctuary_on_one(self):
        '''
        Test case of mystic sanctuary played turn one, island and Treasure Hunt in hand for turn two
        '''
        game = GameStateObject()
        game.islands = 1
        game.lands = 1
        game.hand = [TREASURE_HUNT, BASIC_ISLAND]

        game.decide_main_phase_actions()
        ioctp = game.indices_of_cards_to_play

        expected_actions = [[1, None], [0, TREASURE_HUNT]]
        self.assertEqual(expected_actions, ioctp,
            "game player should've played island then treasure hunt")

    def test_thassas_oracle_and_mystic_sanctuary_in_hand(self):
        '''
        If hand doesn't contain lonely sandbar or treasure hunt but has thassa's oracle
        and mystic sanctuary and there are three islands in play, should play mystic
        santuary to retrieve a treasure hunt from yard
        '''
        game = GameStateObject()
        game.islands = 3
        game.lands = 3
        game.treasure_hunts_played = 1
        game.yard = [TREASURE_HUNT]
        game.hand = [THASSAS_ORACLE, MYSTIC_SANCTUARY, BASIC_ISLAND]

        game.decide_main_phase_actions()
        ioctp = game.indices_of_cards_to_play

        expected_actions = [[1, MYSTIC_SANCTUARY]]
        self.assertEqual(expected_actions, ioctp)

class TestLogParser(unittest.TestCase):
    '''Test cases for log_parser.py'''
    def setUp(self):
        # TODO: make this mock logging actually work
        mock_writer = MagicMock()
        # open = MagicMock(return_value=mock_writer)
        patch("builtins.open", mock_open(mock=mock_writer, read_data=None))

    def test_get_opening_hand(self):
        '''Read opening hand from log'''
        mouse_controller.mulligan = MagicMock()

        log = read_log_from_file('log_with_opening_hand')
        game = GameStateObject()

        log_parser.parse_log(log, game)

        expected_hand = [BASIC_ISLAND] * 7
        self.assertEqual(expected_hand, game.hand, \
            "game hand should've been updated to match expected_hand")
        mouse_controller.mulligan.assert_called()

    def test_get_card_draw(self):
        '''Read card draw for turn from log'''
        # Pretend that log doesn't also contain main phase 1
        log_parser.is_player_phase = MagicMock(return_value=False)

        log = read_log_from_file('log_with_card_for_turn')
        game = GameStateObject()

        log_parser.parse_log(log, game)

        self.assertEqual([BASIC_ISLAND], game.hand, \
            "game hand should've been updated with card drawn")

    def test_identify_cycling_available(self):
        '''
        Identify log which indicates cycling is available and ensure that Next/Pass
        button is clicked in this case.
        '''
        mouse_controller.click_submit = MagicMock()
        log = read_log_from_file('log_with_cycling_available_during_main')
        game = GameStateObject()
        game.played_cards_for_turn = True

        log_parser.parse_log(log, game)

        self.assertEqual([], game.indices_of_cards_to_play)
        mouse_controller.click_submit.assert_called()

    def test_identify_cycling_available2(self):
        '''
        Identify log which indicates cycling is available and ensure that Next/Pass
        button is clicked in this case.
        '''
        mouse_controller.click_submit = MagicMock()
        log = read_log_from_file('log_with_cycling_available_during_main2')
        game = GameStateObject()
        game.played_cards_for_turn = True

        log_parser.parse_log(log, game)

        self.assertEqual([], game.indices_of_cards_to_play)
        mouse_controller.click_submit.assert_called()


class TestExecutor(unittest.TestCase):
    '''Test cases that combine the logger and player'''
    def setUp(self):
        mouse_controller.close_revealed_cards = MagicMock()
        mouse_controller.click_submit = MagicMock()
        mouse_controller.mulligan = MagicMock()
        mouse_controller.keepHand = MagicMock()
        mouse_controller.pass_priority = MagicMock()
        mouse_controller.play_card = MagicMock()
        mouse_controller.tap_all_lands = MagicMock()
        mouse_controller.wait_for_discard_message = MagicMock()
        mouse_controller.wait_for_priority_after_casting_treasure_hunt = MagicMock()
        time.sleep = MagicMock()
        log_parser.play_card = MagicMock()

    def test_turn_one_mystic_sanctuary(self):
        '''
        Mock log_generator to read logs corresponding to mystic sanctuary turn one,island turn two
        '''
        logs_to_read = []
        for i in range(1, 11):
            logs_to_read.append(read_log_from_file(f'mystic{i}'))
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)
        log_parser.update_hand_after_playing_treasure_hunt = MagicMock(return_value=[])

        play_game()

        log_parser.update_hand_after_playing_treasure_hunt.assert_called()

    def test_key_error_on_card_draw(self):
        '''Run through logs that produced key error on get_drawn_card_from_log'''
        logs_to_read = retrieve_logs_from_directory('logs_index_out_of_bounds_error')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)

        play_game()

    def test_index_out_of_bounds_mystic_sanctuary(self):
        '''
        Run through logs that produced index out of bounds error while popping
        treasure hunt after retrieving it with mystic sanctuary
        '''
        logs_to_read = retrieve_logs_from_directory( \
            'logs_index_out_of_bounds_after_mystic_sanctuary')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)
        log_parser.update_hand_after_playing_treasure_hunt = MagicMock( \
            return_value=[BASIC_ISLAND, LONELY_SANDBAR, THASSAS_ORACLE, MYSTIC_SANCTUARY])

        play_game()

    def test_end_turn_when_starting_with_just_treasure_hunt(self):
        '''Start turn one with just treasure hunt and ensure player clicks end turn'''
        logs_to_read = retrieve_logs_from_directory('logs_on_the_play_one_card_in_hand')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)

        play_game()

        mouse_controller.click_submit.assert_called()

    def test_key_error_reading_initial_hand(self):
        '''Key error reading a hand while deciding to mulligan'''
        mouse_controller.concede = MagicMock()
        logs_to_read = retrieve_logs_from_directory('logs_key_error_reading_hand')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)

        play_game()

        mouse_controller.concede.assert_not_called()

    def test_play_card_at_position_outside_hand(self):
        '''Player tried to play card at position 5 with only 5 cards in hand'''
        mouse_controller.concede = MagicMock()
        logs_to_read = retrieve_logs_from_directory('logs_didnt_play_turn_one')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)

        play_game()

        mouse_controller.concede.assert_not_called()

    def test_doesnt_play_on_turn_one(self):
        '''On the play with 2x island, 2x lonely sandbar, treasure hunt but did nothing'''
        logs_to_read = retrieve_logs_from_directory('logs_didnt_play_turn_one')
        log_crawler.create_game_log_generator = MagicMock(return_value=logs_to_read)

        play_game()

        log_parser.play_card.assert_called()


def read_log_from_file(filename: str) -> dict:
    '''Given name of test log file, retrieve it as a dict'''
    current_path = os.getcwd()
    test_logs_subdirectory_path = os.path.join(current_path, 'logs_for_tests')
    with open(os.path.join(test_logs_subdirectory_path, f'{filename}.json')) as log_file:
        log = json.load(log_file)
        return log

def retrieve_logs_from_directory(folder_name: str) -> list:
    '''Given name of directory, create list of dicts from the logs there'''
    current_path = os.getcwd()
    test_logs_subdirectory_path = os.path.join(current_path, folder_name)
    logs = []
    log_number = 0
    read_all_logs = False
    while not read_all_logs:
        log_number += 1
        file_name = f'log{log_number}.json'
        try:
            with open(os.path.join(test_logs_subdirectory_path, file_name)) as log_file:
                print(f'reading log {file_name}')
                logs.append(json.load(log_file))
        except FileNotFoundError:
            read_all_logs = True
    return logs


if __name__ == '__main__':
    unittest.main()
