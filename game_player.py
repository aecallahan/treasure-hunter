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
        self.islands = 0
        self.lands = 0
        self.mana_spent = 0
        self.mulligan_count = 0
        self.treasure_hunts_played = 0
        self.turn = 0
        self.concede = False
        self.mulligan = False
        self.tap_out = False
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
        Return an ordered list of indices of cards in hand to play this turn, as
        well as any special actions associated with that card. Update hand to reflect
        these cards having been played. Pop cards from hand as we go to maintain
        correct card index for mouse_controller as cards get played sequentially.
        '''
        self.mana_spent = 0
        self.tap_out = False
        self.will_discard = False
        indices_of_cards_to_play = []
        if self.treasure_hunts_played == 0 and TREASURE_HUNT not in self.hand:
            self.concede = True
            return []
        if self.lands == 0:
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                indices_of_cards_to_play.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 1:
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
                if TREASURE_HUNT in self.hand:
                    indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                indices_of_cards_to_play.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 2:
            if TREASURE_HUNT in self.hand:
                indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            if BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                indices_of_cards_to_play.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 3:
            if MYSTIC_SANCTUARY in self.hand and LONELY_SANDBAR in self.hand and \
                TREASURE_HUNT in self.yard and self.islands == 3:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
                indices_of_cards_to_play.append(self._cycle())
                indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            elif BASIC_ISLAND in self.hand and TREASURE_HUNT in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
                indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
            elif BASIC_ISLAND in self.hand:
                indices_of_cards_to_play.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
        elif self.lands >= 4:
            if self.treasure_hunts_played == 3:
                if TREASURE_HUNT in self.hand and THASSAS_ORACLE in self.hand:
                    indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
                    indices_of_cards_to_play.append(self._play_spell(THASSAS_ORACLE))
                elif THASSAS_ORACLE in self.hand and MYSTIC_SANCTUARY in self.hand \
                and LONELY_SANDBAR in self.hand:
                    indices_of_cards_to_play.append(self._play_land(MYSTIC_SANCTUARY))
                    indices_of_cards_to_play.append(self._cycle())
                    indices_of_cards_to_play.append(self._play_spell(TREASURE_HUNT))
                    indices_of_cards_to_play.append(self._play_spell(THASSAS_ORACLE))
        self.tap_out = (LONELY_SANDBAR in self.hand and self.lands > self.mana_spent) \
            or self.lands > 1
        return indices_of_cards_to_play

    def _cycle(self):
        card_index = self.hand.index(LONELY_SANDBAR)
        self.hand.pop(card_index)
        action = "CYCLE"
        self.mana_spent += 1
        return [card_index, action]

    def _play_land(self, land_type: str) -> list:
        card_index = self.hand.index(land_type)
        action = None
        if land_type == MYSTIC_SANCTUARY:
            if self.lands >= 3:
                action = MYSTIC_SANCTUARY
                self.yard.remove(TREASURE_HUNT)
            else:
                self.mana_spent += 1
        elif land_type == LONELY_SANDBAR:
            action = LONELY_SANDBAR
            self.mana_spent += 1

        self.lands += 1
        if land_type != LONELY_SANDBAR:
            self.islands += 1
        self.hand.pop(card_index)
        return [card_index, action]

    def _play_spell(self, spell_type: str) -> list:
        if spell_type in self.hand:
            card_index = self.hand.index(spell_type)
            self.yard.append(self.hand.pop(card_index))
        else:
            # If card isn't in hand, it's a treasure hunt that'll be fetched from yard
            card_index = len(self.hand)
        if spell_type == TREASURE_HUNT:
            self.treasure_hunts_played += 1
            self.will_discard = True
        self.mana_spent += 2
        return [card_index, None]
