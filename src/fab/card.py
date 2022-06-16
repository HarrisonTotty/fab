'''
Contains the definition of a Flesh and Blood card.
'''

from __future__ import annotations

import csv
import copy
import dataclasses
import io
import json
import os
import re

from IPython.display import display, Image
from statistics import mean, median, stdev
from typing import Any, Optional
from unidecode import unidecode

CARD_CATALOG: Optional[CardList] = None

RARITY_VALUE: dict[str, int] = {
    'P': 0,
    'T': 1,
    'C': 2,
    'R': 3,
    'S': 4,
    'M': 5,
    'L': 6,
    'F': 7,
}

@dataclasses.dataclass
class Card:
    '''
    Represents a Flesh and Blood card. Each card has the following fields:
      * body - The full body text of the card, excluding flavor text
      * cost - The pitch cost of the card
      * defense - The defense value of the card
      * flavor_text - Any lore flavor text printed on the card
      * full_name - The name of the card, including the pitch value
      * grants - A list of key words this card grants to other cards
      * health - The health value of the card (for heroes and minions)
      * identifiers - A list of card identifiers, such as "RNR012"
      * image_urls - A dictionary of card image URLs, by card identifier.
      * intelligence - The intelligence value of the card (for heroes)
      * keywords - A list of keywords associated with the card, such as "Attack" or "Dominate"
      * name - The name of the card, not including the pitch value
      * pitch - The pitch value of the card
      * power - The "attack" or "power" value of the card
      * rarities - A list of rarities available to the card
      * sets - The list of card set codes associated with this card
      * tags - A collection of user-defined tags associated with the card
      * type_text - The full type box text of the card ("Ninja Action - Attack")
      * types - The list of all types associated with this card
    '''

    body: Optional[str]
    cost: None | str | int
    defense: None | str | int
    flavor_text: Optional[str]
    full_name: str
    grants: list[str]
    health: Optional[int]
    identifiers: list[str]
    image_urls: dict[str, str]
    intelligence: Optional[int]
    keywords: list[str]
    name: str
    pitch: Optional[int]
    power: None | str | int
    rarities: list[str]
    sets: list[str]
    tags: list[str]
    type_text: str
    types: list[str]

    def __getitem__(self, key: str) -> Any:
        '''
        Allows one to access fields of a card via dictionary syntax.
        '''
        return self.__dict__[key]

    def __hash__(self) -> Any:
        '''
        Returns the hash representation of the card.
        '''
        return hash((self.name, self.pitch, self.type_text))

    def __len__(self) -> int:
        '''
        Returns the number of tags associated with this card.
        '''
        return len(self.tags)

    def __str__(self) -> str:
        '''
        Returns the string representation of the transaction. This is an alias
        of the `to_json()` method.
        '''
        return self.to_json()

    @staticmethod
    def from_full_name(full_name: str, catalog: Optional[CardList] = None) -> Card:
        '''
        Creates a new card from its full name. To instantiate the card this way,
        a card catalog (`CardList`) must be provided, defaulting to
        `card.CARD_CATALOG`.
        '''
        _catalog = CARD_CATALOG if catalog is None else catalog
        if _catalog is None: raise Exception('specified card catalog has not been initialized')
        grouped = _catalog.group(by='full_name')
        if not full_name in grouped:
            raise Exception(f'specified card catalog does not contain a card will full name "{full_name}"')
        return copy.deepcopy(grouped[full_name][0])

    @staticmethod
    def from_json(jsonstr: str) -> Card:
        '''
        Creates a new card from the specified JSON string.
        '''
        return Card(**json.loads(jsonstr))

    def image(self, identifier: Optional[str] = None) -> Any:
        '''
        Display an image of this card, optionally providing an alternative
        identifier to use.
        '''
        if not self.image_urls: return 'No images available'
        if isinstance(identifier, str):
            return display(Image(self.image_urls[identifier]))
        else:
            return display(Image(self.image_urls[list(self.image_urls.keys())[-1]]))

    def is_action(self) -> bool:
        '''
        Whether this card is an action card.
        '''
        return 'Action' in self.types

    def is_attack(self) -> bool:
        '''
        Whether this card is an attack card.
        '''
        return 'Attack' in self.types

    def is_attack_reaction(self) -> bool:
        '''
        Whether this card is an attack reaction card.
        '''
        return 'Attack Reaction' in self.types

    def is_aura(self) -> bool:
        '''
        Whether this card is an aura card.
        '''
        return 'Aura' in self.types

    def is_defense_reaction(self) -> bool:
        '''
        Whether this card is a defense reaction card.
        '''
        return 'Defense Reaction' in self.types

    def is_equipment(self) -> bool:
        '''
        Whether this card is an equipment card.
        '''
        return 'Equipment' in self.types

    def is_hero(self) -> bool:
        '''
        Whether this card is a hero card.
        '''
        return 'Hero' in self.types

    def is_instant(self) -> bool:
        '''
        Whether this card is an instant card.
        '''
        return 'Instant' in self.types

    def is_item(self) -> bool:
        '''
        Whether this card is an item card.
        '''
        return 'Item' in self.types

    def is_reaction(self) -> bool:
        '''
        Whether this card is an attack or defense reaction card.
        '''
        return self.is_attack_reaction() or self.is_defense_reaction()

    def is_token(self) -> bool:
        '''
        Whether this card is a token card.
        '''
        return 'Token' in self.types

    def is_weapon(self) -> bool:
        '''
        Whether this card is a weapon card.
        '''
        return 'Weapon' in self.types

    def keys(self) -> list[str]:
        '''
        Returns the dictionary keys associated with this card class.
        '''
        return list(self.__dict__.keys())

    def to_dict(self) -> dict:
        '''
        Converts this card into a raw python dictionary.
        '''
        return copy.deepcopy(self.__dict__)

    def to_json(self) -> str:
        '''
        Converts this card into a JSON string representation.
        '''
        return json.dumps(self.__dict__)


@dataclasses.dataclass
class CardList:
    '''
    Represents a collection of cards.
    '''
    items: list[Card]

    def __getitem__(self, index: int) -> Card:
        '''
        Allows one to access cards using index notation.
        '''
        return self.items[index]

    def __iter__(self):
        '''
        Iterator implementation.
        '''
        yield from self.items

    def __len__(self) -> int:
        '''
        Returns the number of items within this card list.
        '''
        return len(self.items)

    def actions(self) -> CardList:
        '''
        Returns the set of all action cards in this card list.
        '''
        return CardList([card for card in self if card.is_action()])

    def attacks(self) -> CardList:
        '''
        Returns the set of all attack cards in this card list.
        '''
        return CardList([card for card in self if card.is_attack()])

    def attack_reactions(self) -> CardList:
        '''
        Returns the set of all attack reaction cards in this card list.
        '''
        return CardList([card for card in self if card.is_attack_reaction()])

    def auras(self) -> CardList:
        '''
        Returns the set of all aura cards in this card list.
        '''
        return CardList([card for card in self if card.is_aura()])

    def costs(self) -> list[int]:
        '''
        Returns the set of all card costs associated with this list of cards
        (excluding cards with no cost or with variable cost).
        '''
        res = []
        for card in self:
            if isinstance(card.cost, int): res.append(card.cost)
        return list(set(res))

    def counts(self) -> dict[str, int]:
        '''
        Returns a dictionary of card counts organized by full name.
        '''
        counts = {}
        for card in self:
            if card.full_name in counts:
                counts[card.full_name] += 1
            else:
                counts[card.full_name] = 1
        return counts

    def defense_reactions(self) -> CardList:
        '''
        Returns the set of all defense reaction cards in this card list.
        '''
        return CardList([card for card in self if card.is_defense_reaction()])

    def defense_values(self) -> list[int]:
        '''
        Returns the set of all card defense values associated with this list of
        cards (excluding cards with no defense or with variable defense).
        '''
        res = []
        for card in self:
            if isinstance(card.defense, int): res.append(card.defense)
        return list(set(res))

    @staticmethod
    def empty() -> CardList:
        '''
        Returns a new empty card list containing no cards.
        '''
        return CardList([])

    def equipment(self) -> CardList:
        '''
        Returns the set of all equipment cards in this card list.
        '''
        return CardList([card for card in self if card.is_equipment()])

    def filter(self, **kwargs) -> CardList:
        '''
        Filters a list of cards according to a function filtering by:
          * body
          * cost
          * defense
          * full_name
          * grants
          * health
          * intelligence
          * keywords
          * name
          * pitch
          * power
          * sets
          * tags
          * type_text
          * types
        In addition to functions/lambdas, you can also specify:
          * A string for the `body`, `full_name`, `name`, or `type_text` keyword
            arguments. These comparisons are case-insentitive and will match
            substrings.
          * An integer for the `cost`, `defense`, `health`, `intelligence`,
            `pitch`, or `power` keyword arguments. `None` and `str` values
            will not be included in the results.
          * A tuple of integers for the `cost`, `defense`, `health`,
            `intelligence`, `pitch`, or `power` keyword arguments. This defines
            a range of values to include (inclusive).
          * A list of strings for the `grants`, `keywords`, `sets`, `tags`, and
            `types` keyword arguments. At least one value of the list must be
            present for an item to be included.
          * A string for the `grants`, `keywords`, `sets`, `tags`, and `types`
            keyword arguments. This is the same as passing in a single-element
            list.
        If a keyword argument called `negate` is set to `True`, then each filter
        specification is reversed.
        '''
        ALLOWED_KEYS = [
            'body',
            'cost',
            'defense',
            'full_name',
            'grants',
            'health',
            'intelligence',
            'keywords',
            'name',
            'negate',
            'pitch',
            'power',
            'sets',
            'tags',
            'type_text',
            'types'
        ]
        for key in kwargs:
            if not key in ALLOWED_KEYS:
                raise Exception(f'unknown filter key "{key}"')
        if len(self.items) < 2: return copy.deepcopy(self)
        filtered = []
        negate = 'negate' in kwargs and kwargs['negate']
        for c in self:
            if 'body' in kwargs:
                body = kwargs['body']
                if isinstance(body, str):
                    if negate:
                        if body.lower() in str(c.body).lower(): continue
                    else:
                        if not body.lower() in str(c.body).lower(): continue
                else:
                    if negate:
                        if body(c.body): continue
                    else:
                        if not body(c.body): continue
            if 'cost' in kwargs:
                cost = kwargs['cost']
                if isinstance(cost, int):
                    if negate:
                        if isinstance(c.cost, int) and cost == c.cost: continue
                    else:
                        if not isinstance(c.cost, int) or cost != c.cost: continue
                elif isinstance(cost, tuple):
                    if negate:
                        if isinstance(c.cost, int) and c.cost >= cost[0] and c.cost <= cost[1]: continue
                    else:
                        if not isinstance(c.cost, int) or c.cost < cost[0] or c.cost > cost[1]: continue
                else:
                    if negate:
                        if cost(c.cost): continue
                    else:
                        if not cost(c.cost): continue
            if 'defense' in kwargs:
                defense = kwargs['defense']
                if isinstance(defense, int):
                    if negate:
                        if isinstance(c.defense, int) and defense == c.defense: continue
                    else:
                        if not isinstance(c.defense, int) or defense != c.defense: continue
                elif isinstance(defense, tuple):
                    if negate:
                        if isinstance(c.defense, int) and c.defense >= defense[0] and c.defense <= defense[1]: continue
                    else:
                        if not isinstance(c.defense, int) or c.defense < defense[0] or c.defense > defense[1]: continue
                else:
                    if negate:
                        if defense(c.defense): continue
                    else:
                        if not defense(c.defense): continue
            if 'full_name' in kwargs:
                full_name = kwargs['full_name']
                if isinstance(full_name, str):
                    if negate:
                        if full_name.lower() in c.full_name.lower(): continue
                    else:
                        if not full_name.lower() in c.full_name.lower(): continue
                else:
                    if negate:
                        if full_name(c.full_name): continue
                    else:
                        if not full_name(c.full_name): continue
            if 'grants' in kwargs:
                grants = kwargs['grants']
                if isinstance(grants, str):
                    if negate:
                        if grants in c.grants: continue
                    else:
                        if not grants in c.grants: continue
                elif isinstance(grants, list):
                    if negate:
                        if True in [(x in c.grants) for x in grants]: continue
                    else:
                        if not (True in [(x in c.grants) for x in grants]): continue
                else:
                    if negate:
                        if grants(c.grants): continue
                    else:
                        if not grants(c.grants): continue
            if 'health' in kwargs:
                health = kwargs['health']
                if isinstance(health, int):
                    if negate:
                        if isinstance(c.health, int) and health == c.health: continue
                    else:
                        if not isinstance(c.health, int) or health != c.health: continue
                elif isinstance(health, tuple):
                    if negate:
                        if isinstance(c.health, int) and c.health >= health[0] and c.health <= health[1]: continue
                    else:
                        if not isinstance(c.health, int) or c.health < health[0] or c.health > health[1]: continue
                else:
                    if negate:
                        if health(c.health): continue
                    else:
                        if not health(c.health): continue
            if 'intelligence' in kwargs:
                intelligence = kwargs['intelligence']
                if isinstance(intelligence, int):
                    if negate:
                        if isinstance(c.intelligence, int) and intelligence == c.intelligence: continue
                    else:
                        if not isinstance(c.intelligence, int) or intelligence != c.intelligence: continue
                elif isinstance(intelligence, tuple):
                    if negate:
                        if isinstance(c.intelligence, int) and c.intelligence >= intelligence[0] and c.intelligence <= intelligence[1]: continue
                    else:
                        if not isinstance(c.intelligence, int) or c.intelligence < intelligence[0] or c.intelligence > intelligence[1]: continue
                else:
                    if negate:
                        if intelligence(c.intelligence): continue
                    else:
                        if not intelligence(c.intelligence): continue
            if 'keywords' in kwargs:
                keywords = kwargs['keywords']
                if isinstance(keywords, str):
                    if negate:
                        if keywords in c.keywords: continue
                    else:
                        if not keywords in c.keywords: continue
                elif isinstance(keywords, list):
                    if negate:
                        if True in [(x in c.keywords) for x in keywords]: continue
                    else:
                        if not (True in [(x in c.keywords) for x in keywords]): continue
                else:
                    if negate:
                        if keywords(c.keywords): continue
                    else:
                        if not keywords(c.keywords): continue
            if 'name' in kwargs:
                name = kwargs['name']
                if isinstance(name, str):
                    if negate:
                        if name.lower() in c.name.lower(): continue
                    else:
                        if not name.lower() in c.name.lower(): continue
                else:
                    if negate:
                        if name(c.name): continue
                    else:
                        if not name(c.name): continue
            if 'pitch' in kwargs:
                pitch = kwargs['pitch']
                if isinstance(pitch, int):
                    if negate:
                        if isinstance(c.pitch, int) and pitch == c.pitch: continue
                    else:
                        if not isinstance(c.pitch, int) or pitch != c.pitch: continue
                elif isinstance(pitch, tuple):
                    if negate:
                        if isinstance(c.pitch, int) and c.pitch >= pitch[0] and c.pitch <= pitch[1]: continue
                    else:
                        if not isinstance(c.pitch, int) or c.pitch < pitch[0] or c.pitch > pitch[1]: continue
                else:
                    if negate:
                        if pitch(c.pitch): continue
                    else:
                        if not pitch(c.pitch): continue
            if 'power' in kwargs:
                power = kwargs['power']
                if isinstance(power, int):
                    if negate:
                        if isinstance(c.power, int) and power == c.power: continue
                    else:
                        if not isinstance(c.power, int) or power != c.power: continue
                elif isinstance(power, tuple):
                    if negate:
                        if isinstance(c.power, int) and c.power >= power[0] and c.power <= power[1]: continue
                    else:
                        if not isinstance(c.power, int) or c.power < power[0] or c.power > power[1]: continue
                else:
                    if negate:
                        if power(c.power): continue
                    else:
                        if not power(c.power): continue
            if 'sets' in kwargs:
                sets = kwargs['sets']
                if isinstance(sets, str):
                    if negate:
                        if sets in c.sets: continue
                    else:
                        if not sets in c.sets: continue
                elif isinstance(sets, list):
                    if negate:
                        if True in [(x in c.sets) for x in sets]: continue
                    else:
                        if not (True in [(x in c.sets) for x in sets]): continue
                else:
                    if negate:
                        if sets(c.sets): continue
                    else:
                        if not sets(c.sets): continue
            if 'tags' in kwargs:
                tags = kwargs['tags']
                if isinstance(tags, str):
                    if negate:
                        if tags in c.tags: continue
                    else:
                        if not tags in c.tags: continue
                elif isinstance(tags, list):
                    if negate:
                        if True in [(x in c.tags) for x in tags]: continue
                    else:
                        if not (True in [(x in c.tags) for x in tags]): continue
                else:
                    if negate:
                        if tags(c.tags): continue
                    else:
                        if not tags(c.tags): continue
            if 'type_text' in kwargs:
                type_text = kwargs['type_text']
                if isinstance(type_text, str):
                    if negate:
                        if type_text.lower() in c.type_text.lower(): continue
                    else:
                        if not type_text.lower() in c.type_text.lower(): continue
                else:
                    if negate:
                        if type_text(c.type_text): continue
                    else:
                        if not type_text(c.type_text): continue
            if 'types' in kwargs:
                types = kwargs['types']
                if isinstance(types, str):
                    if negate:
                        if types in c.types: continue
                    else:
                        if not types in c.types: continue
                elif isinstance(types, list):
                    if negate:
                        if True in [(x in c.types) for x in types]: continue
                    else:
                        if not (True in [(x in c.types) for x in types]): continue
                else:
                    if negate:
                        if types(c.types): continue
                    else:
                        if not types(c.types): continue
            filtered.append(copy.deepcopy(c))
        return CardList(filtered)

    @staticmethod
    def from_csv(csvstr: str, delimiter: str = '\t') -> CardList:
        '''
        Creates a new list of cards given a CSV string representation.
        '''
        try:
            csv_data = csv.DictReader(io.StringIO(csvstr), delimiter = delimiter)
        except Exception as e:
            raise Exception(f'unable to parse CSV content - {e}')
        def int_str_or_none(inputstr: str) -> int | str | None:
            '''
            A helper function for building out stuff like `cost`, etc.
            '''
            if not inputstr:
                return None
            elif inputstr.isdigit():
                return int(inputstr)
            else:
                return inputstr
        def image_url_parser(inputstr: str) -> dict[str, str]:
            '''
            A helper function for parsing our the image URL dictionary.
            '''
            if not inputstr: return {}
            result = {}
            if ',' in inputstr:
                for substrings in [x.split(' - ', 1) for x in unidecode(inputstr).split(',') if ' - ' in x]:
                    result[substrings[1].strip()] = substrings[0].strip()
            elif ' - ' in inputstr:
                substring = unidecode(inputstr).split(' - ', 1)
                result[substring[1].strip()] = substring[0].strip()
            return result
        cards = []
        for entry in csv_data:
            try:
              cards.append(Card(
                  body         = unidecode(entry['Functional Text'].strip()) if entry['Functional Text'] else None,
                  cost         = int_str_or_none(entry['Cost']),
                  defense      = int_str_or_none(entry['Defense']),
                  flavor_text  = unidecode(entry['Flavor Text'].strip()) if entry['Flavor Text'] else None,
                  full_name    = unidecode(entry['Name'].strip()) + (f" ({entry['Pitch']})" if entry['Pitch'].isdigit() else ''),
                  grants       = [x.strip() for x in entry['Granted Keywords'].split(',')] if entry['Granted Keywords'] else [],
                  health       = int(entry['Health']) if entry['Health'].isdigit() else None,
                  identifiers  = [x.strip() for x in entry['Identifiers'].split(',')],
                  intelligence = int(entry['Intelligence']) if entry['Intelligence'].isdigit() else None,
                  image_urls   = image_url_parser(entry['Image URLs']),
                  keywords     = list(set(([x.strip() for x in entry['Card Keywords'].split(',')] if entry['Card Keywords'] else []) + ([x.strip() for x in entry['Ability and Effect Keywords'].split(',')] if entry['Ability and Effect Keywords'] else []))),
                  name         = unidecode(entry['Name'].strip()),
                  pitch        = int(entry['Pitch']) if entry['Pitch'].isdigit() else None,
                  power        = int_str_or_none(entry['Power']),
                  rarities     = [x.strip() for x in entry['Rarity'].split(',')],
                  sets         = [x.strip() for x in entry['Set Identifiers'].split(',')],
                  tags         = [],
                  type_text    = unidecode(entry['Type Text'].strip()),
                  types        = [x.strip() for x in entry['Types'].split(',')]
               ))
            except Exception as e:
                raise Exception(f'unable to parse intermediate card data - {e} - {entry}')
        return CardList(cards)

    @staticmethod
    def from_json(jsonstr: str) -> CardList:
        '''
        Creates a new list of cards given a JSON string representation.
        '''
        cards = []
        for jcard in json.loads(jsonstr):
            cards.append(Card(**jcard))
        return CardList(cards)

    def full_names(self) -> list[str]:
        '''
        Returns the set of all full card names within this list of cards.
        '''
        return list(set([card.full_name for card in self]))

    def grants(self) -> list[str]:
        '''
        Returns the set of all card grant keywords within this list of cards.
        '''
        res = []
        for card in self:
            res.extend(card.grants)
        return list(set(res))

    def group(self, by: str = 'type_text', include_empty: bool = False) -> dict[Any, CardList]:
        '''
        Groups transactions by one of the following criteria:
          * key = str
            * full_name
            * grants
            * keyword
            * name
            * rarity
            * set
            * type
            * type_text (default)
          * key = int
            * cost
            * defense
            * health
            * intelligence
            * pitch
            * power
        If `include_empty` is set to `False`, any empty groups will be removed.
        '''
        if len(self.items) < 1: return {}
        res = {}
        # str keys
        if by == 'full_name':
            for full_name in self.full_names():
                res[full_name] = CardList([card for card in self if card.full_name == full_name]).sort()
        elif by == 'grants':
            for grants in self.grants():
                res[grants] = CardList([card for card in self if grants in card.grants]).sort()
        elif by == 'keyword':
            for keyword in self.keywords():
                res[keyword] = CardList([card for card in self if keyword in card.keywords]).sort()
        elif by == 'name':
            for name in self.names():
                res[name] = CardList([card for card in self if card.name == name]).sort()
        elif by == 'rarity':
            for rarity in self.rarities():
                res[rarity] = CardList([card for card in self if rarity in card.rarities]).sort()
        elif by == 'set':
            for card_set in self.sets():
                res[card_set] = CardList([card for card in self if card_set in card.sets]).sort()
        elif by == 'type':
            for type_val in self.types():
                res[type_val] = CardList([card for card in self if type_val in card.types]).sort()
        elif by == 'type_text':
            for type_text in self.type_texts():
                res[type_text] = CardList([card for card in self if card.type_text == type_text]).sort()
        # int keys
        elif by == 'cost':
            for cost in self.costs():
                res[cost] = CardList([card for card in self if isinstance(card.cost, int) and card.cost == cost]).sort()
        elif by == 'defense':
            for defense in self.defense_values():
                res[defense] = CardList([card for card in self if isinstance(card.defense, int) and card.defense == defense]).sort()
        elif by == 'health':
            for health in self.health_values():
                res[health] = CardList([card for card in self if isinstance(card.health, int) and card.health == health]).sort()
        elif by == 'intelligence':
            for intelligence in self.intelligence_values():
                res[intelligence] = CardList([card for card in self if isinstance(card.intelligence, int) and card.intelligence == intelligence]).sort()
        elif by == 'pitch':
            for pitch in self.pitch_values():
                res[pitch] = CardList([card for card in self if isinstance(card.pitch, int) and card.pitch == pitch]).sort()
        elif by == 'power':
            for power in self.power_values():
                res[power] = CardList([card for card in self if isinstance(card.power, int) and card.power == power]).sort()
        return res

    def health_values(self) -> list[int]:
        '''
        Returns the set of all card health values associated with this list of
        cards (excluding cards with no health or with variable health).
        '''
        res = []
        for card in self:
            if isinstance(card.health, int): res.append(card.health)
        return list(set(res))

    def heroes(self) -> CardList:
        '''
        Returns the set of all hero cards in this card list.
        '''
        return CardList([card for card in self if card.is_hero()])

    def identifiers(self) -> list[str]:
        '''
        Returns the set of all card identifiers in this card list.
        '''
        res = []
        for card in self:
            res.extend(card.identifiers)
        return list(set(res))

    def instants(self) -> CardList:
        '''
        Returns the set of all instant cards in this card list.
        '''
        return CardList([card for card in self if card.is_instant()])

    def intelligence_values(self) -> list[int]:
        '''
        Returns the set of all card intelligence values associated with this
        list of cards (excluding cards with no intelligence or with variable
        intelligence).
        '''
        res = []
        for card in self:
            if isinstance(card.intelligence, int): res.append(card.intelligence)
        return list(set(res))

    def item_cards(self) -> CardList:
        '''
        Returns the set of all item cards in this card list.
        '''
        return CardList([card for card in self if card.is_item()])

    def keywords(self) -> list[str]:
        '''
        Returns the set of all keywords in this card list.
        '''
        res = []
        for card in self:
            res.extend(card.keywords)
        return list(set(res))

    @staticmethod
    def load(file_path: str, set_catalog: bool = False) -> CardList:
        '''
        Loads a list of cards from the specified `.json` or `.csv` file. If
        `set_catalog` is set to `True`, then a copy of the loaded card list will
        also be set as the default `card.CARD_CATALOG`.
        '''
        with open(os.path.expanduser(file_path), 'r') as f:
            if file_path.endswith('.json'):
                res = CardList.from_json(f.read())
            elif file_path.endswith('.csv'):
                res = CardList.from_csv(f.read())
            else:
                raise Exception('specified file is not a CSV or JSON file')
        if set_catalog:
            global CARD_CATALOG
            CARD_CATALOG = copy.deepcopy(res)
        return res

    def max_cost(self) -> int:
        '''
        Computes the maximum card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_defense(self) -> int:
        '''
        Computes the maximum card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_health(self) -> int:
        '''
        Computes the maximum card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_intelligence(self) -> int:
        '''
        Computes the maximum card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_pitch(self) -> int:
        '''
        Computes the maximum card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_power(self) -> int:
        '''
        Computes the maximum card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return max(array)
        else:
            return 0

    def mean_cost(self, precision: int = 2) -> float:
        '''
        Computes the mean card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_defense(self, precision: int = 2) -> float:
        '''
        Computes the mean card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_health(self, precision: int = 2) -> float:
        '''
        Computes the mean card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the mean card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_pitch(self, precision: int = 2) -> float:
        '''
        Computes the mean card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_power(self, precision: int = 2) -> float:
        '''
        Computes the mean card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def median_cost(self, precision: int = 2) -> float:
        '''
        Computes the median card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_defense(self, precision: int = 2) -> float:
        '''
        Computes the median card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_health(self, precision: int = 2) -> float:
        '''
        Computes the median card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the median card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_pitch(self, precision: int = 2) -> float:
        '''
        Computes the median card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_power(self, precision: int = 2) -> float:
        '''
        Computes the median card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return 0.0
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    @staticmethod
    def merge(*args, unique: bool = False) -> CardList:
        '''
        Merges two or more card lists into a single one. If `unique` is set to
        `True`, then duplicate cards will be deleted.
        '''
        merged = []
        for card_list in args:
            if card_list is None: continue
            for card in card_list:
                if unique and not card in merged:
                    merged.append(card)
                elif not unique:
                    merged.append(card)
        return CardList(merged)

    def min_cost(self) -> int:
        '''
        Computes the minimum card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_defense(self) -> int:
        '''
        Computes the minimum card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_health(self) -> int:
        '''
        Computes the minimum card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_intelligence(self) -> int:
        '''
        Computes the minimum card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_pitch(self) -> int:
        '''
        Computes the minimum card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_power(self) -> int:
        '''
        Computes the minimum card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return min(array)
        else:
            return 0

    def names(self) -> list[str]:
        '''
        Returns the set of all card names in this card list.
        '''
        return list(set([card.name for card in self]))

    def pitch_cost_difference(self) -> int:
        '''
        Returns the difference between the pitch and cost values of all cards. A
        positive integer indicates that on average one generates more pitch
        value than consumes it. This calculation does not take into effect any
        additional pitch/cost a card might incur in its body text.
        '''
        return self.total_pitch() - self.total_cost()

    def pitch_values(self) -> list[int]:
        '''
        Returns the set of all card pitch values associated with this list of
        cards (excluding cards with no pitch or with variable pitch).
        '''
        res = []
        for card in self:
            if isinstance(card.pitch, int): res.append(card.pitch)
        return list(set(res))

    def power_defense_difference(self) -> int:
        '''
        Returns the difference between the power and defense values of all
        cards. A positive integer indicates the deck prefers an offensive
        strategy. This calculation does not take into effect any additional
        power/defense a card might incur in its body text.
        '''
        return self.total_power() - self.total_defense()

    def power_values(self) -> list[int]:
        '''
        Returns the set of all card power values associated with this list of
        cards (excluding cards with no power or with variable power).
        '''
        res = []
        for card in self:
            if isinstance(card.power, int): res.append(card.power)
        return list(set(res))

    def save(self, file_path: str):
        '''
        Saves the list of cards to the specified file path.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            else:
                raise Exception('specified file path is not a JSON file')

    def sort(self, key: Any = 'name', reverse: bool = False) -> CardList:
        '''
        Sorts the list of cards, returning a new sorted collection. If `reverse`
        is set to `True`, then the order is reversed.

        The `key` parameter may be:
          * A function/lambda on each card.
          * A string corresponding to the field to sort by (for example:
            `type_text`). Any `None` values will be shifted to the beginning of
            the resulting `CardList`, or at the end if `reverse` is equal to
            `True`. Note that when specifying `grants`, `keywords`, `tags` or
            `types`, the ordering is based on the _number_ of values within
            those lists. `rarities` is a special case where cards are sorted by
            their highest/lowest rarity value. `identifiers` and `sets` are
            sorted by their first element.
            not implemented.
        '''
        if isinstance(key, str):
            contains_none = []
            to_sort = []
            for card in self:
                if card[key] is None:
                    contains_none.append(copy.deepcopy(card))
                elif isinstance(card[key], str) and key in ['cost', 'defense', 'health', 'intelligence', 'pitch', 'power']:
                    contains_none.append(copy.deepcopy(card))
                else:
                    to_sort.append(copy.deepcopy(card))
            if key in ['identifiers', 'sets']:
                sorted_part = sorted(to_sort, key = lambda x: x[key][0], reverse = reverse)
            elif key in ['grants', 'keywords', 'tags', 'types']:
                sorted_part = sorted(to_sort, key = lambda x: len(x[key]), reverse = reverse)
            elif key == 'rarities':
                sorted_part = sorted(to_sort, key = lambda x: sorted(RARITY_VALUE[y] for y in x[key])[-1] if x[key] else -1, reverse = reverse)
            else:
                sorted_part = sorted(to_sort, key = lambda x: x[key], reverse = reverse)
            if reverse:
                return CardList(sorted_part + contains_none)
            else:
                return CardList(contains_none + sorted_part)
        else:
            return CardList(sorted(copy.deepcopy(self.items), key = key, reverse = reverse))

    def rarities(self) -> list[str]:
        '''
        Returns the set of all card rarities in this card list.
        '''
        res = []
        for card in self:
            res.extend(card.rarities)
        return list(set(res))

    def reactions(self) -> CardList:
        '''
        Returns the set of all attack and defense reaction cards in this card
        list.
        '''
        return CardList([card for card in self if card.is_reaction()])

    def sets(self) -> list[str]:
        '''
        Returns the set of all card sets in this list.
        '''
        card_sets = []
        for card in self:
            card_sets.extend(card.sets)
        return list(set(card_sets))

    def statistics(self, precision: int = 2) -> dict[str, int | float]:
        '''
        Computes helpful statistics associated with this collection of cards.
        The result is a dictionary containing the following keys:
        * count
        * max_[cost, defense, health, intelligence, pitch, power]
        * mean_[cost, defense, health, intelligence, pitch, power]
        * median_[cost, defense, health, intelligence, pitch, power]
        * min_[cost, defense, health, intelligence, pitch, power]
        * pitch_cost_difference
        * power_defense_difference
        * stdev_[cost, defense, health, intelligence, pitch, power]
        * total_[cost, defense, health, intelligence, pitch, power]
        '''
        return {
            'count': len(self.items),
            'max_cost': self.max_cost(),
            'max_defense': self.max_defense(),
            'max_health': self.max_health(),
            'max_intelligence': self.max_intelligence(),
            'max_pitch': self.max_pitch(),
            'max_power': self.max_power(),
            'mean_cost': self.mean_cost(precision),
            'mean_defense': self.mean_defense(precision),
            'mean_health': self.mean_health(precision),
            'mean_intelligence': self.mean_intelligence(precision),
            'mean_pitch': self.mean_pitch(precision),
            'mean_power': self.mean_power(precision),
            'median_cost': self.median_cost(precision),
            'median_defense': self.median_defense(precision),
            'median_health': self.median_health(precision),
            'median_intelligence': self.median_intelligence(precision),
            'median_pitch': self.median_pitch(precision),
            'median_power': self.median_power(precision),
            'min_cost': self.min_cost(),
            'min_defense': self.min_defense(),
            'min_health': self.min_health(),
            'min_intelligence': self.min_intelligence(),
            'min_pitch': self.min_pitch(),
            'min_power': self.min_power(),
            'pitch_cost_difference': self.pitch_cost_difference(),
            'power_defense_difference': self.power_defense_difference(),
            'stdev_cost': self.stdev_cost(precision),
            'stdev_defense': self.stdev_defense(precision),
            'stdev_health': self.stdev_health(precision),
            'stdev_intelligence': self.stdev_intelligence(precision),
            'stdev_pitch': self.stdev_pitch(precision),
            'stdev_power': self.stdev_power(precision),
            'total_cost': self.total_cost(),
            'total_defense': self.total_defense(),
            'total_health': self.total_health(),
            'total_intelligence': self.total_intelligence(),
            'total_pitch': self.total_pitch(),
            'total_power': self.total_power(),
        }

    def stdev_cost(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_defense(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_health(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.health for x in self if isinstance(x.health, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_pitch(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_power(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 2: return 0.0
        array = [x.power for x in self if isinstance(x.power, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def to_json(self) -> str:
        '''
        Converts the list of cards to a JSON string representation.
        '''
        return json.dumps(self.to_list())

    def to_list(self) -> list[dict[str, Any]]:
        '''
        Converts the list of cards into a raw Python list with nested
        dictionaries.
        '''
        return [card.to_dict() for card in self.items]

    def tokens(self) -> CardList:
        '''
        Returns the set of all token cards in this card list.
        '''
        return CardList([card for card in self if card.is_token()])

    def total_cost(self) -> int:
        '''
        Computes the total card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_defense(self) -> int:
        '''
        Computes the total card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_health(self) -> int:
        '''
        Computes the total card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_intelligence(self) -> int:
        '''
        Computes the total card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_pitch(self) -> int:
        '''
        Computes the total card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_power(self) -> int:
        '''
        Computes the total card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return 0
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return sum(array)
        else:
            return 0

    def types(self) -> list[str]:
        '''
        Returns the set of all card types in this card list.
        '''
        res = []
        for card in self:
            res.extend(card.types)
        return list(set(res))

    def type_texts(self) -> list[str]:
        '''
        Returns the set of all type texts in this card list.
        '''
        return list(set([card.type_text for card in self]))

    def weapons(self) -> CardList:
        '''
        Returns the set of all weapon cards in this card list.
        '''
        return CardList([card for card in self if card.is_weapon()])

