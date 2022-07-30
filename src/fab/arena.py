'''
Contains definitions associated with physical play spaces such as the arena.
'''

from __future__ import annotations

import copy
import dataclasses
import random

from typing import Optional

from .card import Card
from .card_list import CardList
from .chain import CombatChain
from .deck import Deck

@dataclasses.dataclass
class Arena:
    '''
    Represents the physical play space containing all card zones of all players.

    Tip: Warning
      In technicality the _Comprehensive Rules_ document defines the arena to be
      the "collection of all the arms, chest, combat chain, head, hero, legs,
      permanent, and weapon zones", and that the "arsenal, banished, deck,
      graveyard, hand, pitch, and stack zones are not part of the arena".
      However for convenience, this library bundles all zones into a single
      object. When reading cards or evaluating game rules, it is important to
      keep this distinction in mind.

    Attributes:
      combat_chain: The global combat chain.
      player_spaces: A `dict` of player spaces, organized by an arbitrary name.
    '''
    combat_chain: CombatChain = CombatChain.empty()
    player_spaces: dict[str, PlayerSpace] = dataclasses.field(default_factory=dict)

    def add_player_space(self, name: str, space: Optional[PlayerSpace] = None) -> None:
        '''
        Adds the specified player's space to the arena.

        Args:
          name: The arbitrary name string of the player to add.
          space: An optional player space instance to assign to the player, creating a new blank one if `None`.
        '''
        if not name in self.player_spaces:
            self.player_spaces[name] = space if not space is None else PlayerSpace()
        else:
            raise Exception(f'player "{name}" already exists in the arena')

    def remove_player_space(self, name: str) -> PlayerSpace:
        '''
        Removes the specified player space, by name.

        Args:
          name: The name of the player space to remove.

        Returns:
          A reference to the `PlayerSpace` object that was removed.
        '''
        if name in self.player_spaces:
            return self.player_spaces.pop(name)
        else:
            raise Exception(f'specified player space "{name}" does not exist')

    def reset_combat_chain(self) -> None:
        '''
        Resets (empties) the global combat chain.
        '''
        self.combat_chain = CombatChain.empty()

    def reset_player_spaces(self) -> None:
        '''
        Resets the player spaces to their original configuration.

        This method calls the `.reset_zones()` method on each player space. See
        that method for more details.
        '''
        for s in self.player_spaces.values():
            s.reset_zones()


@dataclasses.dataclass
class PlayerSpace:
    '''
    Represents the physical play space of card zones and accompanying metadata
    associated with a player.

    Note:
      Despite most usually having only one card, all zones are treated as card
      lists so that certain effects may be tracked properly (like light heroes
      placing cards into their "soul").

      The top card of any zone is considered the last element of that zone's
      list of cards.

    Attributes:
      arms: Any cards in the arms equipment zone.
      arsenal: Any cards currently in the player's arsenal.
      banished: Any cards currently in the player's banished zone.
      chest: Any cards in the chest equipment zone.
      deck: The "main" deck of the player.
      graveyard: Any cards currently in the player's graveyard.
      hand: Any cards currently in the player's hand.
      head: Any cards in the head equipment zone.
      hero: Any cards in the hero zone.
      legs: Any cards in the legs equipment zone.
      permanent: Any cards in the permanent zone (typically active tokens, items, or allies).
      pitch: Any cards currently in the player's pitch zone.
      primary_weapon: Any cards in the primary weapon zone.
      secondary_weapon: Any cards in the secondary weapon zone.
    '''
    arms: CardList = CardList.empty()
    arsenal: CardList = CardList.empty()
    banished: CardList = CardList.empty()
    chest: CardList = CardList.empty()
    deck: CardList = CardList.empty()
    graveyard: CardList = CardList.empty()
    hand: CardList = CardList.empty()
    head: CardList = CardList.empty()
    hero: CardList = CardList.empty()
    legs: CardList = CardList.empty()
    permanent: CardList = CardList.empty()
    pitch: CardList = CardList.empty()
    primary_weapon: CardList = CardList.empty()
    secondary_weapon: CardList = CardList.empty()

    def clear_pitch(self, order: Optional[list[int]] = [], return_to_hand: bool = False) -> None:
        '''
        Clears the pitch zone of cards, placing them on the bottom of the deck.

        If the `order` argument is `None`, then the pitched cards will be placed
        on the bottom of the deck in a random order. Otherwise, a list of
        integers may be specified corresponding to the order of indices. An
        empty list indicates that the order should be preserved.

        Args:
          order: The order in which cards should be returned to the deck, or `None` to randomize the order.
          return_to_hand: Whether to return the pitched cards to the hand rather than placing them in the deck.
        '''
        if not order is None:
            cache = [self.pitch[i] for i in order] if order else copy.deepcopy(self.pitch.data)
        else:
            cache = copy.deepcopy(self.pitch)
            random.shuffle(cache)
        if return_to_hand:
            self.hand.extend(cache)
        else:
            self.deck[:0] = cache
        self.pitch = CardList.empty()

    def draw_hand(self, int_modifier: int = 0) -> None:
        '''
        Draws cards according to the hero card's intelligence.

        This method automatically moves cards from the `deck` field to the `hand`
        field.

        Args:
          int_modifier: An additional value to add to the effective hero intelligence.
        '''
        hero_int = self.hero_card().intelligence
        target_cards = (hero_int if not hero_int is None else 0) + int_modifier
        while len(self.hand) < target_cards:
            self.hand.append(self.deck.pop())

    @staticmethod
    def from_deck(
        deck: Deck,
        arms: Optional[Card | str] = None,
        chest: Optional[Card | str] = None,
        head: Optional[Card | str] = None,
        legs: Optional[Card | str] = None,
        primary_weapon: Optional[Card | str] = None,
        secondary_weapon: Optional[Card | str] = None
    ) -> PlayerSpace:
        '''
        Creates a new player space from the specified deck.

        Args:
          arms: An optional `Card` or full name of a card to place in the arms equipment zone.
          chest: An optional `Card` or full name of a card to place in the chest equipment zone.
          deck: The `Deck` object from which this player space should be constructed.
          head: An optional `Card` or full name of a card to place in the head equipment zone.
          legs: An optional `Card` or full name of a card to place in the legs equipment zone.
          primary_weapon: An optional `Card` or full name of a card to place in the primary weapon zone.
          secondary_weapon: An optional `Card` or full name of a card to place in the secondary weapon zone.

        Returns:
          A new player space from the specified deck.
        '''
        res = PlayerSpace(
            deck = copy.deepcopy(deck.cards),
            hero = CardList([copy.deepcopy(deck.hero)])
        )
        if isinstance(arms, str):
            res.arms = copy.deepcopy(deck.inventory.filter(full_name=arms))
        elif isinstance(arms, Card):
            res.arms.append(copy.deepcopy(arms))
        if isinstance(chest, str):
            res.chest = copy.deepcopy(deck.inventory.filter(full_name=chest))
        elif isinstance(chest, Card):
            res.chest.append(copy.deepcopy(chest))
        if isinstance(head, str):
            res.head = copy.deepcopy(deck.inventory.filter(full_name=head))
        elif isinstance(head, Card):
            res.head.append(copy.deepcopy(head))
        if isinstance(legs, str):
            res.legs = copy.deepcopy(deck.inventory.filter(full_name=legs))
        elif isinstance(legs, Card):
            res.legs.append(copy.deepcopy(legs))
        if isinstance(primary_weapon, str):
            res.primary_weapon = copy.deepcopy(deck.inventory.filter(full_name=primary_weapon))
        elif isinstance(primary_weapon, Card):
            res.primary_weapon.append(copy.deepcopy(primary_weapon))
        if isinstance(secondary_weapon, str):
            res.secondary_weapon = copy.deepcopy(deck.inventory.filter(full_name=secondary_weapon))
        elif isinstance(secondary_weapon, Card):
            res.secondary_weapon.append(copy.deepcopy(secondary_weapon))
        return res

    def hero_card(self) -> Card:
        '''
        Determines the _actual_ hero card within the player space's hero zone.

        Note:
          This is needed because multiple cards may exist in the hero zone.

        Returns:
          The hero card contained in the hero zone.
        '''
        return [card for card in self.hero if card.is_hero()][0]

    def primary_weapon_card(self) -> Card:
        '''
        Determines the _actual_ primary weapon card within the player space's
        primary weapon zone.

        Note:
          This is needed because multiple cards may exist in the primary weapon
          zone.

        Returns:
          The primary weapon card contained in the primary weapon zone.
        '''
        return self.primary_weapon.filter(types=['Weapon', 'Off-Hand'])[0]

    def redraw_hand(self, int_modifier: int = 0) -> None:
        '''
        Shuffles the current hand back into the deck, drawing a new one.

        Args:
          int_modifier: An additional modifier to add to the hero's intelligence value.
        '''
        self.deck.extend(self.hand)
        self.hand = CardList.empty()
        self.shuffle_deck()
        self.draw_hand(int_modifier=int_modifier)

    def reset_zones(self) -> None:
        '''
        Resets the zones of the player space.

        This method moves all cards from the pitch, graveyard and banished zones
        back into the deck (or other appropriate place), which is then shuffled.
        In addition:
          * Any cards in hand will be returned to the deck.
          * Equipment cards will be returned to their appropriate zone.
          * Token cards will deleted.
          * Non-token cards in the permanent zone will be returned to their appropriate zone.
        '''
        collected: CardList = copy.deepcopy(
            self.arms +
            self.arsenal +
            self.banished +
            self.chest +
            self.graveyard +
            self.hand +
            self.head +
            self.hero +
            self.legs +
            self.permanent +
            self.pitch +
            self.primary_weapon +
            self.secondary_weapon
        )
        self.arms = collected.filter(types='Arms')
        self.arsenal = CardList.empty()
        self.banished = CardList.empty()
        self.chest = collected.filter(types='Chest')
        self.graveyard = CardList.empty()
        self.hand = CardList.empty()
        self.head = collected.filter(types='Head')
        self.hero = collected.filter(types='Hero')
        self.legs = collected.filter(types='Legs')
        self.permanent = CardList.empty()
        self.pitch = CardList.empty()
        weapons = collected.filter(types=['Weapon', 'Off-Hand'])
        if len(weapons) == 0:
            self.primary_weapon = CardList.empty()
            self.secondary_weapon = CardList.empty()
        elif len(weapons) == 1:
            self.primary_weapon = weapons
            self.secondary_weapon = CardList.empty()
        elif len(weapons) == 2:
            self.primary_weapon = CardList([weapons[0]])
            self.secondary_weapon = CardList([weapons[1]])
        else:
            raise Exception('somehow the reset_zone method detected more than 2 weapon-zone cards')
        self.deck.extend(
            collected.filter(types=['Arms', 'Chest', 'Head', 'Hero', 'Legs', 'Off-Hand', 'Token', 'Weapon'], negate=True)
        )
        self.shuffle_deck()

    def secondary_weapon_card(self) -> Card:
        '''
        Determines the _actual_ secondary weapon card within the player space's
        secondary weapon zone.

        Note:
          This is needed because multiple cards may exist in the secondary weapon
          zone.

        Returns:
          The secondary weapon card contained in the secondary weapon zone.
        '''
        return self.secondary_weapon.filter(types=['Weapon', 'Off-Hand'])[0]

    def shuffle_banished(self) -> None:
        '''
        Shuffles the banished zone in-place.
        '''
        random.shuffle(self.banished)

    def shuffle_deck(self) -> None:
        '''
        Shuffles the deck in-place.
        '''
        random.shuffle(self.deck)

    def shuffle_graveyard(self) -> None:
        '''
        Shuffles the graveyard in-place.
        '''
        random.shuffle(self.graveyard)

    def shuffle_hand(self) -> None:
        '''
        Shuffles the hand in-place.
        '''
        random.shuffle(self.hand)
