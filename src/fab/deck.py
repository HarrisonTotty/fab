'''
Contains the definition of a Flesh and Blood card deck.
'''

from __future__ import annotations

import copy
import dataclasses
import json
import os
import random
import requests

from typing import Any, Optional

from .card import Card, CardList
from .meta import GAME_FORMATS

EXCLUDE_TYPES: list[str] = [
    'Adult',
    'Hero',
    'Young'
]

FABDB_API = 'https://api.fabdb.net/decks'

FABDB_API_ALT = 'https://fabdb.net/api/decks'

FABDB_FORMATS = {
    'blitz': 'B',
    'constructed': 'CC'
}

JSON_INDENT: Optional[int] = 2

MAX_ITERATIONS = 100000

MAX_SAME_CARD: dict[str, int] = {
    'B': 2,
    'C': 2,
    'CC': 3,
    'UPF': 3
}

TARGET_DECK_SIZE: dict[str, int] = {
    'B': 40,
    'C': 40,
    'CC': 60,
    'UPF': 60
}

TARGET_INV_SIZE: dict[str, int] = {
    'B': 11,
    'C': 11,
    'CC': 20,
    'UPF': 20
}

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

    def auto_build(
        self,
        cards: CardList,
        catalog: Optional[CardList] = None,
        honor_counts: bool = False,
        max_generic_count: Optional[int] = None,
        only_legal: bool = True,
        replace: bool = True,
        target_deck_size: Optional[int] = None,
        target_inventory_size: Optional[int] = None,
        target_pitch_cost_difference: Optional[int] = None,
        target_power_defense_difference: Optional[int] = None,
    ) -> None:
        '''
        Automatically populates this deck with cards based on its hero, by
        selecting cards from the specified list.

        This method updates the `Deck` object calling it directly, rather than
        returning any object. Cards are mostly chosen at random, however it will
        ensure that you have at least one card for each inventory slot and meet
        all of the count/type requirements for the deck. Any cards that mention
        a token by name will have that token included.

        For the `target_pitch_cost_difference` and
        `target_power_defense_difference` arguments, randomly selected cards
        will be discarded if they push the relevant statistic away from the
        target value (if not `None`). When selecting a value for cost-pitch, you
        may want to refer to the following formula:

        ```
        target = 0
                 + {total additional cost from card body texts}
                 + {total cost of using equipment}
                 + ({number of times you plan on using weapon} * {cost of using weapon})
                 + ({number of times you plan on using hero ability} * {cost of hero ability})
                 - {additional resource points generated from card body texts}
        ```

        Of course the above formula isn't perfect, but you should get the general
        idea. In theory, a perfectly balanced deck should expect to generate the
        minimum number of resources for their typical combos every turn.
        Currently, this method will "give up" attempting to meet these targets
        after 100 tries and will accept a random card before resuming attempts.

        Note:
          To be able to accurately compare cards, a card `catalog` must be
          provided, defaulting to the global catalog `card.CARD_CATALOG` if
          unspecified.

          This method ignores the current legality of the deck's hero.

        Args:
          cards: The input list of cards from which to choose from.
          catalog: An optional `CardList` catalog to use instead of the default catalog.
          honor_counts: Whether to honor the number of copies of each card in the specified input list.
          max_generic_count: Overrides the maximum number of generic cards to include in the main deck, defaulting to at most 20% of the deck.
          only_legal: Whether to only select cards that are currently legal (not banned, suspended, or living legend).
          replace: Whether to replace cards that may already exist within the deck.
          target_deck_size: Overrides the target number of cards to include in the main deck.
          target_inventory_size: Overrides the target number of cards to include in the deck's inventory.
          target_pitch_cost_difference: Specifies the target pitch-cost difference of the main deck, or `None` to disable.
          target_power_defense_difference: Specifies the target power-defense difference of the main deck, or `None` to disable.
        '''
        # First, let's set up all of the variables we need to work with.
        related = copy.deepcopy(self.filter_related(cards, catalog=catalog, only_legal=only_legal))
        if self.format == 'C': related.filter(rarities='C')
        related_types = related.types()
        tgt_deck_size = target_deck_size if not target_deck_size is None else TARGET_DECK_SIZE[self.format]
        tgt_inv_size  = target_inventory_size if not target_inventory_size is None else TARGET_INV_SIZE[self.format]
        max_gen       = max_generic_count if not max_generic_count is None else tgt_deck_size // 5
        curr_deck     = copy.deepcopy(self.cards) if not replace else CardList.empty()
        curr_inv      = copy.deepcopy(self.inventory) if not replace else CardList.empty()
        curr_tokens   = copy.deepcopy(self.tokens) if not replace else CardList.empty()
        curr_iterations = 0
        # Start by building up our inventory.
        while len(curr_inv) < tgt_inv_size:
            curr_iterations += 1
            if curr_iterations > MAX_ITERATIONS: raise Exception('hit maximum iterations while building deck inventory')
            curr_inv_types = curr_inv.types()
            if not 'Weapon' in curr_inv_types and 'Weapon' in related_types:
                choice = random.choice(related.filter(types='Weapon'))
            elif not 'Head' in curr_inv_types and 'Head' in related_types:
                choice = random.choice(related.filter(types='Head'))
            elif not 'Legs' in curr_inv_types and 'Legs' in related_types:
                choice = random.choice(related.filter(types='Legs'))
            elif not 'Arms' in curr_inv_types and 'Arms' in related_types:
                choice = random.choice(related.filter(types='Arms'))
            elif not 'Chest' in curr_inv_types and 'Chest' in related_types:
                choice = random.choice(related.filter(types='Chest'))
            else:
                choice = random.choice(related.filter(types=['Equipment', 'Weapon']))
            curr_inv.append(choice)
            if honor_counts: related.remove(choice)
        # Now lets build up our main deck.
        pitch_cost_attempts = 0
        power_def_attempts  = 0
        while len(curr_deck) < tgt_deck_size:
            curr_iterations += 1
            if curr_iterations > MAX_ITERATIONS: raise Exception('hit maximum iterations while building main deck')
            counts = curr_deck.counts()
            curr_gen = len(curr_deck.filter(types='Generic'))
            choice = random.choice(related.filter(types=['Equipment', 'Weapon', 'Token'], negate=True))
            if counts.get(choice.full_name, 0) >= MAX_SAME_CARD[self.format]: continue
            if 'Generic' in choice.types and curr_gen >= max_gen: continue
            curr_stats = curr_deck.statistics()
            if not target_pitch_cost_difference is None and pitch_cost_attempts < 100:
                choice_pitch_cost = (choice.pitch if isinstance(choice.pitch, int) else 0) - (choice.cost if isinstance(choice.cost, int) else 0)
                if curr_stats['pitch_cost_difference'] > target_pitch_cost_difference and choice_pitch_cost > 0:
                    pitch_cost_attempts += 1
                    continue
                if curr_stats['pitch_cost_difference'] < target_pitch_cost_difference and choice_pitch_cost < 0:
                    pitch_cost_attempts += 1
                    continue
                if curr_stats['pitch_cost_difference'] == target_pitch_cost_difference and choice_pitch_cost != 0:
                    pitch_cost_attempts += 1
                    continue
            if not target_power_defense_difference is None and power_def_attempts < 100:
                choice_power_def = (choice.power if isinstance(choice.power, int) else 0) - (choice.defense if isinstance(choice.defense, int) else 0)
                if curr_stats['power_defense_difference'] > target_power_defense_difference and choice_power_def > 0:
                    power_def_attempts += 1
                    continue
                if curr_stats['power_defense_difference'] < target_power_defense_difference and choice_power_def < 0:
                    power_def_attempts += 1
                    continue
                if curr_stats['power_defense_difference'] == target_power_defense_difference and choice_power_def != 0:
                    power_def_attempts += 1
                    continue
            pitch_cost_attempts = 0
            power_def_attempts  = 0
            curr_deck.append(choice)
            if honor_counts: related.remove(choice)
        # Finally make sure we have a copy of any token card that was referenced.
        # We don't need to worry about honoring counts here because we're only
        # adding 1 token.
        for token in related.filter(types='Token'):
            if not token in curr_tokens:
                if any(token.name.lower() in card.body.lower() for card in curr_deck if isinstance(card.body, str)):
                    curr_tokens.append(token)
                elif isinstance(self.hero.body, str) and token.name.lower() in self.hero.body.lower():
                    curr_tokens.append(token)
        # Now replace our current field values.
        self.cards     = curr_deck.sort()
        self.inventory = curr_inv.sort()
        self.tokens    = curr_tokens.sort()


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
    def from_fabdb(url: str, catalog: Optional[CardList] = None) -> Deck:
        '''
        Imports a deck from [FaB DB](https://fabdb.net).

        Decks may be imported by providing either their full URL
        (`https://fabdb.net/decks/VGkQMojg`) or unique identifier (`VGkQMojg`).

        Note:
          To be able to generate cards, a card `catalog` must be provided,
          defaulting to the global catalog `card.CARD_CATALOG` if unspecified.

        Args:
          catalog: An optional `CardList` catalog to use instead of the default catalog.
          url: The full URL or unique identifier of the deck to import.

        Returns:
          The imported `Deck` object.
        '''
        identifier = url.rsplit('/', 1)[-1]
        data = requests.get(f'{FABDB_API}/{identifier}').json()
        deck_list = {}
        for card in data['cards']:
            full_name = card['name']
            if 'resource' in card['stats']:
                full_name += f' ({card["stats"]["resource"]})'
            deck_list[full_name] = card['total']
        return Deck.from_deck_list(
            name = data['name'],
            deck_list = deck_list,
            catalog = catalog,
            format = FABDB_FORMATS.get(data['format'], 'B')
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

    def is_valid(self, ignore_hero_legality: bool = False, ignore_legality: bool = False) -> tuple[bool, Optional[str]]:
        '''
        Returns whether this is a valid and legal deck given its format.

        Tip: Warning
          This function currently does not validate any restrictions printed on
          cards themselves (ex: "Legendary" cards). Also, any restrictions on
          card rarity might not be accurate, since cards may be printed in
          multiple rarities.

        Args:
          ignore_hero_legality: Whether to ignore the current legal status of the hero card.
          ignore_legality: Whether to ignore the current legal status of cards (not including the hero).

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
        if not ignore_hero_legality:
            if not self.hero.is_legal(self.format): return (False, f'{GAME_FORMATS[self.format]}: Hero "{self.hero.name}" is not currently legal in this format.')
        if any(not card.is_token() for card in self.tokens): return (False, 'Common: Token deck contains non-token cards - move these cards to their appropriate field.')
        if not 'Shapeshifter' in self.hero.types:
            valid_types = self.valid_types()
            for card in self.all_cards(include_tokens=True):
                if card == self.hero: continue
                if not any(t in valid_types for t in card.types): return (False, f'Common: Card "{card.full_name}" is not one of the following types: {valid_types}')
        if not ignore_legality:
            for card in all_cards:
                if card == self.hero: continue
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

    @staticmethod
    def search_fabdb(hero: Card | str, cursor: Optional[str] = None, format: str = 'B', kind: Optional[str] = 'competitive', max_results: int = 30, order: str = 'popular-all') -> dict[str, Any]:
        '''
        Searches [FaB DB](https://fabdb.net) for decks matching the specified constraints.

        The result of this method is a `dict` containing two primary keys:

          * `cursor` - A `str` which may be re-passed to the method (along with
            the same set of other arguments) to retrieve the "next page" of
            results.
          * `decks` - A `list` of deck specifications.

        Each deck specification is also a `dict` containing the following keys:

          * `creator` - The FaB DB user name of the deck creator.
          * `format` - The game format associated with the deck.
          * `gem_id` - The Gem ID of the deck creator (if available).
          * `hero` - The full name of the hero.
          * `id` - The ID of the deck, as would be passed to
            `Deck.from_fabdb()`.
          * `kind` - The kind of deck.
          * `name` - The name of the deck.
          * `notes` - Any notes associated with the deck (in markdown format).
          * `url` - The full URL corresponding to the deck.

        Args:
          cursor: An optional cursor string for iterating through multi-page responses.
          format: The game format identifier (as would be specified for `Deck` objects).
          hero: A `Card` or full name string corresponding to the target hero.
          kind: The type of deck to search for (`"casual"`, `"competitive"`, `"janky"`, `"meme"`, or `None` for no restriction).
          max_results: The maximum number of results to include in the response.
          order: The method by which to order search results (`"newest"`, `"popular-7"`, or `"popular-all"`).

        Returns:
          The results of the search.
        '''
        if max_results > 100:
            raise Exception('please do not exceed 100 max results per request')
        hero_name = hero if isinstance(hero, str) else hero.full_name
        if not format in GAME_FORMATS:
            raise Exception(f'specified format code is not one of {list(GAME_FORMATS.keys())}')
        fabdb_format = [k for k, v in FABDB_FORMATS.items() if v == format][0]
        fabdb_kind = '' if kind is None else kind
        full_url = f'{FABDB_API_ALT}?hero={hero_name}&order={order}&label={fabdb_kind}&format={fabdb_format}&per_page={max_results}'
        if not cursor is None:
            full_url += f'&cursor={cursor}'
        data = requests.get(full_url).json()
        decks = []
        for d in data['data']:
            decks.append({
                'creator': d['user']['name'],
                'format': FABDB_FORMATS[d['format']],
                'gem_id': int(d['user']['gemId']) if d['user']['gemId'] else None,
                'hero': d['hero']['name'],
                'id': d['slug'],
                'kind': d['label'],
                'name': d['name'],
                'notes': d['notes'] if d['notes'] else None,
                'url': f'https://fabdb.net/decks/{d["slug"]}',
            })
        return {
            'cursor': data['links']['next'].rsplit('=', 1)[-1] if not data['links']['next'] is None else None,
            'decks': decks
        }


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
