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
        self.indices_of_cards_to_discard = []
        self.indices_of_cards_to_play = []
        self.yard = []
        self.islands = 0
        self.lands = 0
        self.mana_spent = 0
        self.mulligan_count = 0
        self.system_seat_id = 0
        self.treasure_hunts_played = 0
        self.turn = 0
        self.accepted_hand = False
        self.concede = False
        self.mulligan = False
        self.played_cards_for_turn = False
        self.tap_out = False
        self.will_discard = False

    def reset_game(self):
        '''Reset game state'''
        self.__init__()

    def decide_discard(self):
        '''
        Check hand at end of turn if treasure hunt has been played and decides
        if discarding is required and what to discard if so.
        '''
        ioctd = self.indices_of_cards_to_discard
        remaining_discards = len(self.hand) - 7
        lonely_sandbar_count = 0
        mystic_sanctuary_count = 0
        for index, card in enumerate(self.hand):
            if remaining_discards <= 0:
                break
            if card == BASIC_ISLAND:
                ioctd.append(index)
                remaining_discards -= 1
            elif card == LONELY_SANDBAR:
                if lonely_sandbar_count > 1:
                    ioctd.append(index)
                    remaining_discards -= 1
                else:
                    lonely_sandbar_count += 1
            elif card == MYSTIC_SANCTUARY:
                if mystic_sanctuary_count > 1:
                    ioctd.append(index)
                    remaining_discards -= 1
                else:
                    mystic_sanctuary_count += 1

        # Update hand to remove all cards to be discarded
        for index in reversed(ioctd):
            self.hand.pop(index)
        self.indices_of_cards_to_discard = ioctd

    def decide_mulligan(self):
        '''
        Keep hands containing Treasure Hunt. Concede if mulliganing to 1 card and
        it's not Treasure Hunt.
        '''
        self.mulligan = TREASURE_HUNT not in self.hand
        print(f"self.mulligan_count: {self.mulligan_count}")
        self.concede =self.mulligan_count >= 6 and self.mulligan

    def decide_main_phase_actions(self):
        '''
        Return an ordered list of indices of cards in hand to play this turn, as
        well as any special actions associated with that card. Update hand to reflect
        these cards having been played. Pop cards from hand as we go to maintain
        correct card index for mouse_controller as cards get played sequentially.
        '''
        self.mana_spent = 0
        self.tap_out = False
        self.will_discard = False
        self.indices_of_cards_to_discard = []
        self.indices_of_cards_to_play = []
        self.played_cards_for_turn = True
        ioctp = self.indices_of_cards_to_play

        if self.treasure_hunts_played == 0 and TREASURE_HUNT not in self.hand:
            self.concede = True
        elif self.lands == 0:
            if BASIC_ISLAND in self.hand:
                ioctp.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                ioctp.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                ioctp.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 1:
            if BASIC_ISLAND in self.hand:
                ioctp.append(self._play_land(BASIC_ISLAND))
                if TREASURE_HUNT in self.hand:
                    ioctp.append(self._play_spell(TREASURE_HUNT))
            elif MYSTIC_SANCTUARY in self.hand:
                ioctp.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                ioctp.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 2:
            if TREASURE_HUNT in self.hand:
                ioctp.append(self._play_spell(TREASURE_HUNT))
            if BASIC_ISLAND in self.hand:
                ioctp.append(self._play_land(BASIC_ISLAND))
            elif MYSTIC_SANCTUARY in self.hand:
                ioctp.append(self._play_land(MYSTIC_SANCTUARY))
            elif LONELY_SANDBAR in self.hand:
                ioctp.append(self._play_land(LONELY_SANDBAR))
        elif self.lands == 3:
            if MYSTIC_SANCTUARY in self.hand and LONELY_SANDBAR in self.hand and \
                TREASURE_HUNT in self.yard and self.islands == 3:
                ioctp.append(self._play_land(MYSTIC_SANCTUARY))
                ioctp.append(self._cycle())
                ioctp.append(self._play_spell(TREASURE_HUNT))
            elif BASIC_ISLAND in self.hand and TREASURE_HUNT in self.hand:
                ioctp.append(self._play_land(BASIC_ISLAND))
                ioctp.append(self._play_spell(TREASURE_HUNT))
            elif MYSTIC_SANCTUARY in self.hand:
                ioctp.append(self._play_land(MYSTIC_SANCTUARY))
            elif BASIC_ISLAND in self.hand:
                ioctp.append(self._play_land(BASIC_ISLAND))
        elif self.lands >= 4:
            if self.treasure_hunts_played == 3:
                if TREASURE_HUNT in self.hand and THASSAS_ORACLE in self.hand:
                    ioctp.append(self._play_spell(TREASURE_HUNT))
                    ioctp.append(self._play_spell(THASSAS_ORACLE))
                elif THASSAS_ORACLE in self.hand and MYSTIC_SANCTUARY in self.hand \
                and LONELY_SANDBAR in self.hand:
                    ioctp.append(self._play_land(MYSTIC_SANCTUARY))
                    ioctp.append(self._cycle())
                    ioctp.append(self._play_spell(TREASURE_HUNT))
                    ioctp.append(self._play_spell(THASSAS_ORACLE))
            elif self.treasure_hunts_played < 3:
                if MYSTIC_SANCTUARY in self.hand and LONELY_SANDBAR in self.hand and \
                  TREASURE_HUNT in self.yard and self.islands >= 3:
                    ioctp.append(self._play_land(MYSTIC_SANCTUARY))
                    ioctp.append(self._cycle())
                    ioctp.append(self._play_spell(TREASURE_HUNT))
                elif TREASURE_HUNT in self.hand and BASIC_ISLAND in self.hand:
                    ioctp.append(self._play_land(BASIC_ISLAND))
                    ioctp.append(self._play_spell(TREASURE_HUNT))
            else:
                self.concede = True

        self.tap_out = (LONELY_SANDBAR in self.hand and self.lands > self.mana_spent) \
            or self.lands > 1
        self.indices_of_cards_to_play = ioctp

    def _cycle(self):
        card_index = self.hand.index(LONELY_SANDBAR)
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
        return [card_index, action]

    def _play_spell(self, spell_type: str) -> list:
        if spell_type in self.hand:
            card_index = self.hand.index(spell_type)
            self.yard.append(self.hand[card_index])
        else:
            # If card isn't in hand, it's a treasure hunt that'll be fetched from yard
            card_index = len(self.hand)
        if spell_type == TREASURE_HUNT:
            self.treasure_hunts_played += 1
        self.mana_spent += 2
        return [card_index, spell_type]
