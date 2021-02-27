'''
Handles logic of playing games.
'''

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
        self.mulligan_count = 0
        self.turn = 0
        self.concede = False
        self.mulligan = False

    def reset_game(self):
        '''Reset game state'''
        self.__init__()

    def decide_mulligan(self):
        '''
        Keep hands containing Treasure Hunt. Concede if mulliganing to 1 card and
        it's not Treasure Hunt.
        '''
        self.mulligan = TREASURE_HUNT not in self.hand
        self.concede = len(self.hand) == 1 and self.mulligan

    def main_phase_actions(self):
        '''
        Return an ordered list of indices of cards in hand to play this turn.
        Update hand to reflect these cards having been played. Pop cards from
        hand as we go to maintain correct card index for mouse_controller as
        cards get played sequentially.
        '''
        indices_of_cards_to_play = []
        if BASIC_ISLAND in self.hand:
            indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
        elif MYSTIC_SANCTUARY in self.hand:
            indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        if TREASURE_HUNT in self.hand and self.lands >= 2:
            indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
        return indices_of_cards_to_play

    def _play_land(self, land_type: str) -> int:
        card_index = self.hand.index(land_type)
        self.lands += 1
        self.hand.pop(card_index)
        return card_index

    def _play_spell(self, spell_type: str) -> int:
        card_index = self.hand.index(spell_type)
        self.yard.append(self.hand.pop(card_index))
        return card_index
