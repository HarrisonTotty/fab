'''
Contains the definition of a Flesh and Blood card deck.
'''

from __future__ import annotations

import dataclasses
import json

from typing import Any, Optional

from .card import Card, CardList

VALID_FORMATS = [
    'Blitz',
    'Classic Constructed',
    'Commoner',
    'Ulimate Pit Fight'
]

EXCLUDE_TYPES = [
    'Adult',
    'Hero',
    'Young'
]

@dataclasses.dataclass
class Deck:
    '''
    Represents a deck of Flesh and Blood cards. Each deck has the following
    fields:
      * cards - The "main" part of the deck from which one draws cards
      * format - The game format associated with this deck, being `blitz`, `cc`,
                 `commoner`, or `upf`.
      * hero - The hero card associated with this deck
      * inventory - The list of weapon/equipment cards associated with this deck
                    (not including items).
      * name - An arbitrary name for the deck
      * tokens - Any token cards associated with this deck
    '''

    name: str
    hero: Card
    cards: CardList = CardList.empty()
    format: str = 'Blitz'
    inventory: CardList = CardList.empty()
    tokens: CardList = CardList.empty()

    def __getitem__(self, index: int) -> Card:
        '''
        Allows one to access cards form the "main" part of the deck using index notation.
        '''
        return self.cards[index]

    def __iter__(self):
        '''
        Iterator implementation over the "main" part of the deck.
        '''
        yield from self.cards

    def __len__(self) -> int:
        '''
        Returns the total number of cards within this deck, excluding tokens or
        the hero.
        '''
        return len(self.cards) + len(self.inventory)

    def all_cards(self, include_tokens: bool = False) -> CardList:
        '''
        Returns all cards within this deck (excluding tokens by default).
        '''
        if include_tokens:
            return CardList.merge(CardList([self.hero]), self.inventory, self.cards, self.tokens)
        else:
            return CardList.merge(CardList([self.hero]), self.inventory, self.cards)

    def filter_related(self, cards: CardList, include_generic: bool = True) -> CardList:
        '''
        Filters out cards from the specified list which may be included in this
        deck, based on the deck's hero card. If `include_generic` is set to
        `False`, then `Generic` cards will not be added to the result.
        '''
        return cards.filter(types=self.valid_types(include_generic))

    @staticmethod
    def from_deck_list(name: str, deck_list: dict[str, int], catalog: Optional[CardList] = None, format: str = 'Blitz') -> Deck:
        '''
        Constructs a deck from the given deck list dictionary, where keys
        correspond to the full name of a card and values are their counts. To be
        able to generate cards, a card `catalog` must be provided, defaulting to
        the global catalog `card.CARD_CATALOG` if unspecified.
        '''
        cards: list[Card] = []
        inventory: list[Card] = []
        tokens: list[Card] = []
        hero: Optional[Card] = None
        for full_name, count in deck_list.items():
            for _ in range(0, count):
                card = Card.from_full_name(full_name, catalog)
                if card.is_hero(): hero = card
                elif card.is_equipment() or card.is_weapon(): inventory.append(card)
                elif card.is_token(): tokens.append(card)
                else: cards.append(card)
        if hero is None:
            raise Exception('specified catalog does not contain a hero card')
        return Deck(
            cards = CardList(cards),
            format = format,
            hero = hero,
            inventory = CardList(inventory),
            name = name,
            tokens = CardList(tokens)
        )

    @staticmethod
    def from_json(jsonstr: str) -> Deck:
        '''
        Parses a new deck from a given JSON string representation.
        '''
        data = json.loads(jsonstr)
        return Deck(
            cards     = CardList([Card(**c) for c in data['cards']]),
            format    = data['format'],
            hero      = Card(**data['hero']),
            inventory = CardList([Card(**c) for c in data['inventory']]),
            name      = data['name'],
            tokens    = CardList([Card(**c) for c in data['tokens']])
        )

    def is_valid(self) -> tuple[bool, Optional[str]]:
        '''
        Returns whether this is a valid deck given its format.
        Returns a tuple of the form `(<answer>, <reason>)`.

        This function currently does not validate any restrictions printed on
        cards themselves (ex: "Legendary" cards). Also, any restrictions on card
        rarity might not be accurate, since cards may be printed in multiple
        rarities.
        '''
        all_cards = self.all_cards()
        # Common
        if not self.format in VALID_FORMATS: return (False, f'Common: Specified deck format is not one of {VALID_FORMATS}.')
        if len(self.cards) < 1: return (False, 'Common: Deck does not contain any "main" cards.')
        if any(card.is_equipment() or card.is_weapon() or card.is_hero() for card in self.cards): return (False, 'Common: Main deck contains invalid cards (like equipment) - move these cards to their appropriate field, even when playing Classic Constructed.')
        if len(self.inventory) < 1: return (False, 'Common: Deck does not contain any inventory cards.')
        if any(not (card.is_equipment() or card.is_weapon()) for card in self.inventory): return (False, 'Common: Inventory deck contains non-equipment/weapon cards - move these cards to their appropriate field.')
        if not self.hero.is_hero(): return (False, 'Common: Deck `hero` is not a hero card.')
        if any(not card.is_token() for card in self.tokens): return (False, 'Common: Token deck contains non-token cards - move these cards to their appropriate field.')
        if self.format == 'Blitz':
            if len(self.cards) != 40: return (False, 'Blitz: Main deck may only contain 40 cards.')
            if len(self.inventory) > 11: return (False, 'Blitz: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types: return (False, 'Blitz: Deck must use a "young" hero.')
            if any(v > 2 for v in all_cards.counts().values()): return (False, 'Blitz: Only up to two copies of each unique card are allowed.')
        elif self.format == 'Classic Constructed':
            if len(self) > 80: return (False, 'Classic Constructed: Deck may not contain more than 80 cards (including inventory).')
            if len(self.cards) < 60: return (False, 'Classic Constructed: Main Deck must contain at least 60 cards (excluding inventory).')
            if any(v > 3 for v in all_cards.counts().values()): return (False, 'Classic Constructed: Only up to three copies of each unique card are allowed.')
        elif self.format == 'Commoner':
            if len(self.cards) != 40: return (False, 'Commoner: Main deck may only contain 40 cards.')
            if len(self.inventory) > 11: return (False, 'Commoner: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types: return (False, 'Commoner: Deck must use a "young" hero.')
            if any(v > 2 for v in all_cards.counts().values()): return (False, 'Commoner: Only up to two copies of each unique card are allowed.')
            if any(not 'C' in card.rarities for card in self.cards): return (False, 'Commoner: Main deck may only contain "Common" cards.')
        elif self.format == 'Ultimate Pit Fight':
            return (True, 'Ultimate Pit Fight: Warning, UPF has not been implemented, only common checks have been validated.')
        return (True, None)

    def statistics(self, precision: int = 2) -> dict[str, Any]:
        '''
        Computes useful statistics associated with this deck, returning the
        following keys:
          * card_statistics
            `CardList.statistics()` on the "main" deck of cards, with health and
            intelligence metrics removed.
          * hero
            Contains the intelligence and health of the deck's hero.
          * inventory_statistics
            `CardList.statistics()` on the inventory cards, with health,
            intelligence, cost, and pitch metrics removed since they aren't
            applicable.
        '''
        card_stats = self.cards.statistics(precision)
        inventory_stats = self.inventory.statistics(precision)
        return {
            'card_statistics': {k: v for k, v in card_stats.items() if not any(m in k for m in ['health', 'intelligence'])},
            'hero': {
                'health': self.hero.health,
                'intelligence': self.hero.intelligence
            },
            'inventory_statistics': {k: v for k, v in inventory_stats.items() if not any(m in k for m in ['cost', 'health', 'intelligence', 'pitch'])},
        }

    def to_deck_list(self, include_tokens: bool = False) -> dict[str, int]:
        '''
        Returns a deck-list dictionary for this deck. The keys of this
        dictionary correspond to the full names (including pitch value) of
        cards, while the values are their corresponding counts.
        '''
        return self.all_cards(include_tokens).counts()

    def to_dict(self)-> dict[str, Any]:
        '''
        Returns the raw dictionary form of the deck.
        '''
        return {
            'cards': self.cards.to_list(),
            'format': self.format,
            'hero': self.hero.to_dict(),
            'inventory': self.inventory.to_list(),
            'name': self.name,
            'tokens': self.tokens.to_list()
        }

    def to_json(self) -> str:
        '''
        Returns the JSON string representation of the deck.
        '''
        return json.dumps(self.to_dict())

    def valid_types(self, include_generic: bool = True) -> list[str]:
        '''
        Returns the set of valid card types which may be included in this deck,
        based on the deck's hero card. If `include_generic` is set to `False`,
        then `Generic` will not be added as a valid type.
        '''
        selection = [t for t in self.hero.types if not t in EXCLUDE_TYPES]
        if include_generic:
            return selection + ['Generic']
        else:
            return selection
