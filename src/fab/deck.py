'''
Contains the definition of a Flesh and Blood card deck.
'''

from __future__ import annotations

import dataclasses
import json
import os

from typing import Any, Optional

from .card import Card, CardList
from .meta import GAME_FORMATS

EXCLUDE_TYPES: list[str] = [
    'Adult',
    'Hero',
    'Young'
]

JSON_INDENT: Optional[int] = 2

@dataclasses.dataclass
class Deck:
    '''
    Represents a deck of Flesh and Blood cards.

    Attributes:
      cards: The "main" part of the deck from which one draws cards.
      format: The game format code associated with the deck (see `meta.GAME_FORMATS`).
      hero: The hero card associated with the deck.
      inventory: The list of weapon/equipment cards associated with the deck (not including items).
      name: An arbitrary name for the deck.
      tokens: Any token cards associated with the deck.
    '''

    name: str
    hero: Card
    cards: CardList = CardList.empty()
    format: str = 'B'
    inventory: CardList = CardList.empty()
    tokens: CardList = CardList.empty()

    def __getitem__(self, index: int | slice) -> Card | CardList:
        '''
        Allows one to access cards form the "main" part of the deck using index
        notation.

        Args:
          index: An `int` or `slice` to reference a particular `Card` or sub-`CardList`.

        Returns:
          A particular `Card` if `index` is an `int`, otherwise a `CardList` if `index` is a `slice`.
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

        Returns:
          The number of "main" deck and inventory cards.
        '''
        return len(self.cards) + len(self.inventory)

    def all_cards(self, include_tokens: bool = False) -> CardList:
        '''
        Returns all cards within this deck (excluding tokens by default).

        Args:
          include_tokens: Whether to include token cards in the result.

        Returns:
          A single `CardList` object containing all cards in the deck.
        '''
        res = CardList([self.hero]) + self.inventory + self.cards
        if include_tokens:
            return res + self.tokens
        else:
            return res

    def filter_related(self, cards: CardList, catalog: Optional[CardList] = None, include_generic: bool = True, only_legal: bool = True) -> CardList:
        '''
        Filters out cards from the specified list which may be included in this
        deck, based on the deck's hero card.

        Tip: Warning
          This method does not validate the legality of the deck's hero card.

        Note:
          To be able to accurately compare cards, a card `catalog` must be
          provided, defaulting to the global catalog `card.CARD_CATALOG` if
          unspecified.

        Args:
          cards: The list of cards to filter.
          catalog: An optional `CardList` catalog to use instead of the default catalog.
          include_generic: Whether to include _Generic_ cards in the result.
          only_legal: Whether to include only cards that are currently legal (not banned, suspended, or living legend).

        Returns:
          A subset of the specified card list that work with the deck's hero.
        '''
        initial = CardList._hero_filter_related(
            hero            = self.hero,
            cards           = cards,
            catalog         = catalog,
            include_generic = include_generic
        )
        if only_legal:
            return CardList([card for card in initial if card.is_legal(self.format)])
        else:
            return initial

    @staticmethod
    def from_deck_list(name: str, deck_list: dict[str, int], catalog: Optional[CardList] = None, format: str = 'B') -> Deck:
        '''
        Constructs a deck from the given deck list dictionary, where keys
        correspond to the full name of a card and values are their counts.

        Note:
          To be able to generate cards, a card `catalog` must be provided,
          defaulting to the global catalog `card.CARD_CATALOG` if unspecified.

        Args:
          name: The arbitrary name for the new `Deck`.
          deck_list: The deck list to create the `Deck` from.
          catalog: An optional `CardList` catalog to use instead of the default catalog.
          format: The game format of the deck, being any valid `Deck.format`.

        Returns:
          A new `Deck` built from the specified deck list.
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

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `Deck` from the parsed data.
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

        Tip: Warning
          This function currently does not validate any restrictions printed on
          cards themselves (ex: "Legendary" cards). Also, any restrictions on
          card rarity might not be accurate, since cards may be printed in
          multiple rarities.

        Returns:
          A `tuple` of the form `(<answer>, <reason>)`.
        '''
        all_cards = self.all_cards()
        # Common
        if not self.format in GAME_FORMATS: return (False, f'Common: Specified deck format code is not one of {list(GAME_FORMATS.keys())}.')
        if len(self.cards) < 1: return (False, 'Common: Deck does not contain any "main" cards.')
        if any(card.is_equipment() or card.is_weapon() or card.is_hero() for card in self.cards): return (False, 'Common: Main deck contains invalid cards (like equipment) - move these cards to their appropriate field, even when playing Classic Constructed.')
        if len(self.inventory) < 1: return (False, 'Common: Deck does not contain any inventory cards.')
        if any(not (card.is_equipment() or card.is_weapon()) for card in self.inventory): return (False, 'Common: Inventory deck contains non-equipment/weapon cards - move these cards to their appropriate field.')
        if not self.hero.is_hero(): return (False, 'Common: Deck `hero` is not a hero card.')
        if not self.hero.is_legal(self.format): return (False, f'{GAME_FORMATS[self.format]}: Hero "{self.hero.name}" is not currently legal in this format.')
        if any(not card.is_token() for card in self.tokens): return (False, 'Common: Token deck contains non-token cards - move these cards to their appropriate field.')
        if not 'Shapeshifter' in self.hero.types:
            valid_types = self.valid_types()
            for card in self.all_cards(include_tokens=True):
                if card == self.hero: continue
                if not any(t in valid_types for t in card.types): return (False, f'Common: Card "{card.full_name}" is not one of the following types: {valid_types}')
        for card in all_cards:
            if not card.is_legal(self.format):
                return (False, f'{GAME_FORMATS[self.format]}: Card "{card.full_name}" is not currently legal in this format.')
        if self.format == 'B':
            if len(self.cards) != 40: return (False, 'Blitz: Main deck may only contain 40 cards.')
            if len(self.inventory) > 11: return (False, 'Blitz: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types: return (False, 'Blitz: Deck must use a "young" hero.')
            if any(v > 2 for v in all_cards.counts().values()): return (False, 'Blitz: Only up to two copies of each unique card are allowed.')
        elif self.format == 'CC':
            if len(self) > 80: return (False, 'Classic Constructed: Deck may not contain more than 80 cards (including inventory).')
            if len(self.cards) < 60: return (False, 'Classic Constructed: Main Deck must contain at least 60 cards (excluding inventory).')
            if any(v > 3 for v in all_cards.counts().values()): return (False, 'Classic Constructed: Only up to three copies of each unique card are allowed.')
        elif self.format == 'C':
            if len(self.cards) != 40: return (False, 'Commoner: Main deck may only contain 40 cards.')
            if len(self.inventory) > 11: return (False, 'Commoner: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types: return (False, 'Commoner: Deck must use a "young" hero.')
            if any(v > 2 for v in all_cards.counts().values()): return (False, 'Commoner: Only up to two copies of each unique card are allowed.')
            if any(not 'C' in card.rarities for card in self.cards): return (False, 'Commoner: Main deck may only contain "Common" cards.')
        elif self.format == 'UPF':
            return (True, 'Ultimate Pit Fight: Warning, UPF has not been implemented, only common checks have been validated.')
        return (True, None)

    @staticmethod
    def load(file_path: str, name: Optional[str] = None, format: Optional[str] = None) -> Deck:
        '''
        Loads a deck from the specified JSON or TXT file.

        Note:
          When loading from a TXT file, the name and format of the deck must
          be specified. TXT files loaded by this method expect a file with
          entries of the following form separated by new lines:

          ```
          {count} {full_name}
          ```

          where `count` is the number of copies of the specified card and
          `full_name` is the full name of the card (see `Card.full_name`).

        Args:
          file_path: The file path from which to load.
          name: The name of the resulting deck, if loading from TXT file.
          format: The format code of the resulting deck, if loading from TXT file.

        Returns:
          A new `Deck` object from the loaded data.
        '''
        with open(os.path.expanduser(file_path), 'r') as f:
            if file_path.endswith('.json'):
                return Deck.from_json(f.read())
            elif file_path.endswith('.txt'):
                if name is None or format is None:
                    raise Exception('"name" and "format" must be specified when loading a deck from TXT file')
                deck_list = {}
                for l in f.readlines():
                    if not l.strip(): continue
                    ls = l.strip().split(' ', 1)
                    deck_list[ls[1].strip()] = int(ls[0].strip())
                return Deck.from_deck_list(name, deck_list, format=format)
            else:
                raise Exception('specified file path is not a JSON or TXT file')

    def save(self, file_path: str):
        '''
        Saves this deck to the specified JSON or TXT file.

        Args:
          file_path: The file path to save to.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            elif file_path.endswith('.txt'):
                for k, v in self.to_deck_list():
                    f.write(f'{v} {k}\n')
            else:
                raise Exception('specified file path is not a JSON or TXT file')

    def statistics(self, precision: int = 2) -> dict[str, Any]:
        '''
        Computes useful statistics associated with this deck, returning the
        following keys:

        * `card_statistics` - `CardList.statistics()` on the "main" deck of cards, with health and
          intelligence metrics removed.
        * `hero` - Contains the intelligence and health of the deck's hero.
        * `inventory_statistics` - `CardList.statistics()` on the inventory cards, with health,
          intelligence, cost, and pitch metrics removed since they aren't applicable.

        Returns:
          A `dict` encapsulating the analysis results.
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
        Returns a deck-list dictionary for this deck.

        The keys of this dictionary correspond to the full names (including
        pitch value) of cards, while the values are their corresponding counts.

        Args:
          include_tokens: Whether to include token cards in the deck list.

        Returns:
          The deck-list representation of the deck.
        '''
        return self.all_cards(include_tokens).counts()

    def to_dict(self)-> dict[str, Any]:
        '''
        Returns the raw dictionary form of the deck.

        Returns:
          A raw `dict` containing only Python primitives representing the deck.
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

        Returns:
          The JSON string representation of the deck.
        '''
        return json.dumps(self.to_dict(), indent=JSON_INDENT)

    def valid_types(self, include_generic: bool = True) -> list[str]:
        '''
        Returns the set of valid card types which may be included in this deck,
        based on the deck's hero card.

        Args:
          include_generic: Whether to include the _Generic_ type in the result.

        Returns:
          A `list` of valid card type strings.
        '''
        if 'Shapeshifter' in self.hero.types:
            raise Exception(f'deck hero "{self.hero.full_name}" is a Shapeshifter')
        selection = [t for t in self.hero.types if not t in EXCLUDE_TYPES]
        if include_generic:
            return selection + ['Generic']
        else:
            return selection
