'''
Handles logic of playing games.
'''

BASIC_ISLAND = "Basic Island"
LONELY_SANDBAR = "Lonely Sandbar"
TREASURE_HUNT = "Treasure Hunt"
MYSTIC_SANCTUARY = "Mystic Sanctuary"
THASSAS_ORACLE = "Thassa's Oracle"

cardIdNames = {
    652: BASIC_ISLAND,
    10826: LONELY_SANDBAR,
    24877: TREASURE_HUNT,
    414466: MYSTIC_SANCTUARY,
    419870: THASSAS_ORACLE,
}


class GameStateObject:
    '''Represents the state of a mtg game'''
    def __init__(self):
        self.hand = []
        self.yard = []
        self.lands = 0
        self.mulligan_count = 0
        self.treasure_hunts_played = 0
        self.turn = 0
        self.concede = False
        self.mulligan = False
        self.mystic_sanctuary_action = False
        self.will_discard = False

    def reset_game(self):
        '''Reset game state'''
        self.__init__()

    def decide_mulligan(self):
        '''
        Keep hands containing Treasure Hunt. Concede if mulliganing to 1 card and
        it's not Treasure Hunt.
        '''
        self.mulligan = TREASURE_HUNT not in self.hand
        print(f"self.mulligan_count: {self.mulligan_count}")
        self.concede =self.mulligan_count >= 6 and self.mulligan

    def main_phase_actions(self):
        '''
        Return an ordered list of indices of cards in hand to play this turn.
        Update hand to reflect these cards having been played. Pop cards from
        hand as we go to maintain correct card index for mouse_controller as
        cards get played sequentially.
        '''
        self.will_discard = False
        indices_of_cards_to_play = []
        if self.lands == 0:
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        elif self.lands == 1:
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
                if TREASURE_HUNT in self.hand:
                    indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        elif self.lands == 2:
            if TREASURE_HUNT in self.hand:
                indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        elif self.lands == 3:
            if MYSTIC_SANCTUARY in self.hand and TREASURE_HUNT in self.yard:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
                self.mystic_sanctuary_action = True
                self.yard.remove(TREASURE_HUNT)
            elif BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        return indices_of_cards_to_play

    def _play_land(self, land_type: str) -> int:
        card_index = self.hand.index(land_type)
        self.lands += 1
        self.hand.pop(card_index)
        return card_index

    def _play_spell(self, spell_type: str) -> int:
        card_index = self.hand.index(spell_type)
        self.yard.append(self.hand.pop(card_index))
        if spell_type == TREASURE_HUNT:
            self.treasure_hunts_played += 1
            self.will_discard = True
        return card_index
