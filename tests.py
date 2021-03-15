'''unit tests'''
import json
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from game_player import GameStateObject
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
        self.assertEqual(expected_actions, ioctp, \
            "game player should've played island then treasure hunt")

class TestLogParser(unittest.TestCase):
    '''Test cases for log_parser.py'''
    def setUp(self):
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


def read_log_from_file(filename: str) -> dict:
    '''Given name of test log file, retrieve it as a dict'''
    current_path = os.getcwd()
    test_logs_subdirectory_path = os.path.join(current_path, 'logs_for_tests')
    with open(os.path.join(test_logs_subdirectory_path, f'{filename}.json')) as log_file:
        log = json.load(log_file)
        return log


if __name__ == '__main__':
    unittest.main()
