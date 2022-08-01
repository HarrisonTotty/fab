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

from IPython.display import display, Markdown
from typing import Any, cast, Optional

from .card import Card
from .card_list import CardList
from .meta import GAME_FORMATS, TALENT_SUPERTYPES

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
    'D': 2,
    'UPF': 3
}

TARGET_DECK_SIZE: dict[str, int] = {
    'B': 40,
    'C': 40,
    'CC': 60,
    'D': 30,
    'UPF': 60
}

TARGET_INV_SIZE: dict[str, int] = {
    'B': 11,
    'C': 11,
    'CC': 20,
    'D': 5,
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
      notes: Any additional notes to include about the deck, in Markdown format.
      tokens: Any token cards associated with the deck.
    '''

    name: str
    hero: Card
    cards: CardList = CardList.empty()
    format: str = 'B'
    inventory: CardList = CardList.empty()
    notes: Optional[str] = None
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

    def add_card(self, card: Card, count: int = 1) -> None:
        '''
        Adds the specified card to the deck.

        Tip: Warning
          The specified `count` will be ignored when adding inventory or tokens.

        Args:
          card: The card to add.
          count: The number of copies of the card to add.
        '''
        if count < 1:
            raise ValueError('please specify a positive integer value for "count"')
        if card.is_hero():
            raise Exception('this method does not accept hero cards')
        for _ in range(_, count):
            if card.is_equipment() or card.is_weapon():
                if not card in self.inventory:
                    self.inventory.append(card)
            elif card.is_token():
                if not card in self.tokens:
                    self.tokens.append(card)
            else:
                self.cards.append(card)

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
        cards: Optional[CardList] = None,
        color_weights: Optional[tuple[int, int, int]] = None,
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
        selecting cards from the specified list or pulling from the default
        card catalog.

        This method updates the `Deck` object calling it directly, rather than
        returning any object. Cards are mostly chosen at random, however it will
        ensure that you have at least one card for each inventory slot and meet
        all of the count/type requirements for the deck. Any cards that mention
        a token by name will have that token included.

        One may provide a `tuple[int, int, int]` to the `color_weights` argument
        to skew the probability that cards will be chosen based on their color.
        The weights of this `tuple` are of the form `(<red>, <yellow>, <blue>)`.
        As an example, providing `color_weights=(1, 0, 3)` implies that on
        average your deck should contain three blue cards for every one red card
        and zero yellow cards. A weight of `0` completely removes the chance
        that color will make it into the deck.

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
          To be able to accurately compare cards, the default card catalog must
          be initialized.

          This method ignores the current legality of the deck's hero.

        Args:
          cards: The input list of cards from which to choose from, or `None` to pull from the default card catalog.
          color_weights: Specifies a random choice weight bias when randomly selecting cards, by card color (see above).
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
        supporting_cards = self.supporting_cards(only_legal=only_legal)
        related = copy.deepcopy(
            supporting_cards if cards is None else CardList(card for card in cards if card in supporting_cards)
        )
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
            weighted = related if color_weights is None else CardList.empty()
            if not color_weights is None:
                for card in related:
                    if card.pitch is None or isinstance(card.pitch, str):
                        weighted.append(card)
                    else:
                        target_weight = color_weights[card.pitch - 1]
                        if target_weight < 0:
                            raise ValueError('target weights must be zero or a positive integer')
                        for _ in range(0, target_weight):
                            weighted.append(card)
            choice = random.choice(weighted.filter(types=['Equipment', 'Weapon', 'Token'], negate=True))
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
                if any(token.name in card.token_keywords for card in curr_deck):
                    curr_tokens.append(token)
                elif token.name in self.hero.token_keywords:
                    curr_tokens.append(token)
        # Now replace our current field values.
        self.cards     = curr_deck.sort()
        self.inventory = curr_inv.sort()
        self.tokens    = curr_tokens.sort()

    def clear(self, include_inventory: bool = False, include_tokens: bool = False) -> None:
        '''
        Clears this deck of cards, optionally also including inventory/tokens.

        Args:
          include_inventory: Whether to also clear the deck's inventory cards.
          include_tokens: Whether to also clear the deck's token cards.
        '''
        self.cards = CardList.empty()
        if include_inventory:
            self.inventory = CardList.empty()
        if include_tokens:
            self.tokens = CardList.empty()

    @staticmethod
    def from_deck_list(name: str, deck_list: dict[str, int], format: str = 'B', notes: Optional[str] = None) -> Deck:
        '''
        Constructs a deck from the given deck list dictionary, where keys
        correspond to the full name of a card and values are their counts.

        Note:
          To be able to generate cards, the default card catalog must be
          available.

        Args:
          name: The arbitrary name for the new `Deck`.
          deck_list: The deck list to create the `Deck` from.
          format: The game format of the deck, being any valid `Deck.format`.
          notes: Any additional notes to include with the deck, in Markdown format.

        Returns:
          A new `Deck` built from the specified deck list.
        '''
        cards: list[Card] = []
        inventory: list[Card] = []
        tokens: list[Card] = []
        hero: Optional[Card] = None
        for full_name, count in deck_list.items():
            for _ in range(0, count):
                card = Card.from_full_name(full_name)
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
            notes = notes,
            tokens = CardList(tokens)
        )

    @staticmethod
    def from_fabdb(url: str) -> Deck:
        '''
        Imports a deck from [FaB DB](https://fabdb.net).

        Decks may be imported by providing either their full URL
        (`https://fabdb.net/decks/VGkQMojg`) or unique identifier (`VGkQMojg`).

        Note:
          To be able to generate cards, the default card catalog must be
          initialized.

        Args:
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
            format = FABDB_FORMATS.get(data['format'], 'B'),
            notes = data['notes'] if data['notes'] else None
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
            cards     = CardList.from_list(data['cards']),
            format    = data['format'],
            hero      = Card.from_dict(data['hero']),
            inventory = CardList.from_list(data['inventory']),
            name      = data['name'],
            notes     = data.get('notes'),
            tokens    = CardList.from_list(data['tokens'])
        )

    def is_valid(
        self,
        ignore_copy_limits: bool = False,
        ignore_hero_legality: bool = False,
        ignore_inv_size_limits: bool = False,
        ignore_legality: bool = False,
        ignore_size_limits: bool = False,
    ) -> tuple[bool, Optional[str]]:
        '''
        Returns whether this is a valid and legal deck given its format.

        Unless otherwise specified, in general this method ensures:

          1. The deck contains at least one hero, inventory card, and main deck
             card.
          2. The deck has a valid game format code.
          3. The deck doesn't have any invalid card placements (like inventory
             cards in the main deck).
          4. All cards (including hero) are currently legal for play.
          5. Main deck and inventory deck sizes conform to the specified format.
          6. The deck doesn't contain too many copies of a particular card
             (according to the specified format).
          7. The deck only contains cards which adhere to the specified format's
             rarity requirements.

        Tip: Warning
          This function currently does not validate any restrictions printed on
          cards themselves (ex: "Legendary" cards). Also, any restrictions on
          card rarity might not be accurate, since cards may be printed in
          multiple rarities.

        Args:
          ignore_copy_limits: Whether to ignore limits around the allowed number of card copies.
          ignore_hero_legality: Whether to ignore the current legal status of the hero card.
          ignore_inv_size_limits: Whether to ignore any maximum/minimum inventory deck size limits.
          ignore_legality: Whether to ignore the current legal status of cards (not including the hero).
          ignore_size_limits: Whether to ignore any maximum/minimum size limits of the main deck.

        Returns:
          A `tuple` of the form `(<answer>, <reason>)`.
        '''
        all_cards = self.all_cards()
        # Common
        if not self.format in GAME_FORMATS: return (False, f'Common: Specified deck format code is not one of {list(GAME_FORMATS.keys())}.')
        if not ignore_size_limits and len(self.cards) < 1: return (False, 'Common: Deck does not contain any "main" cards.')
        if any(card.is_equipment() or card.is_weapon() or card.is_hero() for card in self.cards): return (False, 'Common: Main deck contains invalid cards (like equipment) - move these cards to their appropriate field, even when playing Classic Constructed.')
        if not ignore_inv_size_limits and len(self.inventory) < 1: return (False, 'Common: Deck does not contain any inventory cards.')
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
            if not ignore_size_limits and len(self.cards) != 40:
                return (False, 'Blitz: Main deck may only contain 40 cards.')
            if not ignore_inv_size_limits and len(self.inventory) > 11:
                return (False, 'Blitz: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types:
                return (False, 'Blitz: Deck must use a "young" hero.')
            if not ignore_copy_limits and any(v > 2 for v in all_cards.counts().values()):
                return (False, 'Blitz: Only up to two copies of each unique card are allowed.')
        elif self.format == 'C':
            if not ignore_size_limits and len(self.cards) != 40:
                return (False, 'Commoner: Main deck may only contain 40 cards.')
            if not ignore_inv_size_limits and len(self.inventory) > 11:
                return (False, 'Commoner: Inventory deck may not contain more than 11 cards.')
            if not 'Young' in self.hero.types:
                return (False, 'Commoner: Deck must use a "young" hero.')
            if not ignore_copy_limits and any(v > 2 for v in all_cards.counts().values()):
                return (False, 'Commoner: Only up to two copies of each unique card are allowed.')
            if any(not 'C' in card.rarities for card in self.cards):
                return (False, 'Commoner: Main deck may only contain "Common" cards.')
        elif self.format == 'CC':
            if not ignore_size_limits and not ignore_inv_size_limits:
                if len(self) > 80:
                    return (False, 'Classic Constructed: Deck may not contain more than 80 cards (including inventory).')
                if len(self.cards) < 60:
                    return (False, 'Classic Constructed: Main Deck must contain at least 60 cards (excluding inventory).')
            elif not ignore_size_limits and ignore_inv_size_limits:
                if len(self.cards) > 80:
                    return (False, 'Classic Constructed: Main Deck may not contain more than 80 cards (when ignoring inventory deck size).')
                if len(self.cards) < 60:
                    return (False, 'Classic Constructed: Main Deck must contain at least 60 cards (excluding inventory).')
            elif ignore_size_limits and not ignore_inv_size_limits:
                if len(self.inventory) > 20:
                    return (False, 'Classic Constructed: Inventory deck cannot contain more than 20 cards (when ignoring main deck size).')
            if not ignore_copy_limits and any(v > 3 for v in all_cards.counts().values()):
                return (False, 'Classic Constructed: Only up to three copies of each unique card are allowed.')
        elif self.format == 'D':
            if not ignore_size_limits and len(self.cards) < 30:
                return (False, 'Draft: Main deck must contain at least 30 cards.')
            if not 'Young' in self.hero.types:
                return (False, 'Draft: Deck must use a "young" hero.')
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

    def render_notes(self) -> Any:
        '''
        Renders the notes of this deck as a Markdown cell.

        Returns:
          The IPython-rendered markdown output.
        '''
        if not self.notes is None:
            return display(Markdown(self.notes))
        else:
            raise Exception('specified deck does not contain any notes')

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

        * `card_statistics` - `CardList.statistics()` on the "main" deck of
          cards, with intellect and life value metrics removed.
        * `hero` - Contains the intellect and life value of the deck's hero.
        * `inventory_statistics` - `CardList.statistics()` on the inventory
          cards, with intellect, life value, resource cost, and pitch value
          metrics removed since they aren't applicable.

        Returns:
          A `dict` encapsulating the analysis results.
        '''
        card_stats = self.cards.statistics(precision)
        inventory_stats = self.inventory.statistics(precision)
        return {
            'card_statistics': {k: v for k, v in card_stats.items() if not any(m in k for m in ['intellect', 'life'])},
            'hero': {
                'intellect': self.hero.intellect,
                'life': self.hero.life
            },
            'inventory_statistics': {k: v for k, v in inventory_stats.items() if not any(m in k for m in ['cost', 'intellect', 'life', 'pitch'])},
        }

    def supporting_cards(self, include_generic: bool = True, only_legal: bool = True) -> CardList:
        '''
        Returns the list of all cards which may be used in this deck.

        Tip: Warning
          This method does not validate the legality of the deck's hero card.

        Note:
          This method requires the default card catalog to be initialized.

        Args:
          include_generic: Whether to include _Generic_ cards in the result.
          only_legal: Whether to include only cards that are currently legal (not banned, suspended, or living legend).

        Returns:
          A subset of all cards that work with the deck's hero.
        '''
        if cast(str, self.hero.class_type) == 'Shapeshifter':
            raise Exception(f'deck hero "{self.hero.name}" is a shapeshifter')
        from .catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('default catalog has not been initialized')
        hero_class = cast(str, self.hero.class_type)
        hero_talent = self.hero.talent_type
        cards = DEFAULT_CATALOG.lookup_cards(key='types', value='Generic') if include_generic else CardList.empty()
        cards.extend(
            card for card in DEFAULT_CATALOG.lookup_cards(key='class_type', value=hero_class) if card.talent_type is None
        )
        if not hero_talent is None:
            cards.extend(
                card for card in DEFAULT_CATALOG.lookup_cards(key='talent_type', value=hero_talent) if card.class_type is None or card.class_type == hero_class
            )
        if 'Essense' in self.hero.ability_keywords:
            for keyword in self.hero.type_keywords:
                if keyword in TALENT_SUPERTYPES and keyword != hero_talent:
                    cards.extend(
                        card for card in DEFAULT_CATALOG.lookup_cards(key='talent_type', value=keyword) if card.class_type is None or card.class_type == hero_class
                    )
        dedup = CardList.empty()
        for card in cards:
            if not 'Hero' in card.types and not card in dedup:
                if only_legal and card.is_legal(self.format):
                    dedup.append(card)
                elif not only_legal:
                    dedup.append(card)
        return dedup

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
            'notes': self.notes,
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
        types = ['Generic', cast(str, self.hero.class_type)] if include_generic else []
        if not self.hero.talent_type is None:
            types.append(self.hero.talent_type)
        if 'Essence' in self.hero.ability_keywords:
            types.extend(t for t in self.hero.type_keywords if t in TALENT_SUPERTYPES)
        return types
