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

from statistics import mean, median, stdev
from typing import Any, Optional

@dataclasses.dataclass
class Card:
    '''
    Represents a Flesh and Blood card. Each card has the following fields:
      * body - The full body text of the card, excluding flavor text
      * cost - The pitch cost of the card
      * defense - The defense value of the card
      * flavor_text - Any lore flavor text printed on the card
      * grants - A list of key words this card grants to other cards
      * health - The health value of the card (for heroes and minions)
      * identifiers - A list of card identifiers, such as "RNR012"
      * intelligence - The intelligence value of the card (for heroes)
      * keywords - A list of keywords associated with the card, such as "Attack" or "Dominate"
      * name - The name of the card, not including the pitch value
      * pitch - The pitch value of the card
      * power - The "attack" or "power" value of the card
      * rarities - A list of rarities available to the card
      * sets - The list of card set codes associated with this card
      * tags - A collection of user-defined tags associated with the card
      * type_text - The full type text of the card ("Ninja Action - Attack")
      * types - The list of types associated with the type_text
    '''

    body: Optional[str]
    cost: None | str | int
    defense: None | str | int
    flavor_text: Optional[str]
    grants: list[str]
    health: Optional[int]
    identifiers: list[str]
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
    def from_json(jsonstr: str) -> Card:
        '''
        Creates a new card from the specified JSON string.
        '''
        return Card(**json.loads(jsonstr))

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

    def filter(self, **kwargs) -> CardList:
        '''
        Filters a list of cards according to a function filtering by:
          * body
          * cost
          * defense
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
          * A string for the `body`, `name`, or `type_text` keyword arguments.
            These comparisons are case-insentitive and will match substrings.
          * An integer for the `cost`, `defense`, `health`, `intelligence`,
            `pitch`, or `power` keyword arguments. `None` and `str` values
            will not be included in the results.
          * A tuple of integers for the `cost`, `defense`, `health`,
            `intelligence`, `pitch`, or `power` keyword arguments. This defines
            a range of values to include (inclusive).
          * A list of strings for the `grants`, `keywords`, `sets`, `tags`, and
            `types` keyword arguments. At least one value of the list must be
            present for an item to be included.
        If a keyword argument called `negate` is set to `True`, then each filter
        specification is reversed.
        '''
        ALLOWED_KEYS = [
            'body',
            'cost',
            'defense',
            'grants'
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
                        if body.lower() in c.body.lower(): continue
                    else:
                        if not body.lower() in c.body.lower(): continue
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
        cards = []
        for entry in csv_data:
            cards.append(Card(
                body         = entry['Functional Text'].strip() if entry['Functional Text'] else None,
                cost         = int_str_or_none(entry['Cost']),
                defense      = int_str_or_none(entry['Defense']),
                flavor_text  = entry['Flavor Text'] if entry['Flavor Text'] else None,
                grants       = [x.strip() for x in entry['Granted Keywords'].split(',')],
                health       = int(entry['Health']) if entry['Health'].isdigit() else None,
                identifiers  = [x.strip() for x in entry['Identifiers'].split(',')],
                intelligence = int(entry['Intelligence']) if entry['Intelligence'].isdigit() else None,
                keywords     = [x.strip() for x in entry['Card Keywords'].split(',')] + [x.strip() for x in entry['Ability and Effect Keywords'].split(',')],
                name         = entry['Name'].strip(),
                pitch        = int(entry['Pitch']) if entry['Pitch'].isdigit() else None,
                power        = int_str_or_none(entry['Power']),
                rarities     = [x.strip() for x in entry['Rarity'].split(',')],
                sets         = [x.strip() for x in entry['Set Identifiers'].split(',')],
                tags         = [],
                type_text    = entry['Type Text'].strip(),
                types        = [x.strip() for x in entry['Types'].split(',')]
            ))
        return CardList(cards)

    @staticmethod
    def from_json(jsonstr: str) -> CardList:
        '''
        Creates a new list of cards given a JSON string representation.
        '''
        cards = []
        for jcard in json.loads(jsonstr):
            cards.append(Card.from_json(jcard))
        return CardList(cards)

    @staticmethod
    def load(file_path: str) -> CardList:
        '''
        Loads a list of cards from the specified `.json` or `.csv` file.
        '''
        with open(os.path.expanduser(file_path), 'r') as f:
            if file_path.endswith('.json'):
                return CardList.from_json(f.read())
            elif file_path.endswith('.csv'):
                return CardList.from_csv(f.read())
            else:
                raise Exception('specified file is not a CSV or JSON file')

    def max_cost(self) -> Optional[int]:
        '''
        Computes the maximum card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return max(array)
        else:
            return None

    def max_defense(self) -> Optional[int]:
        '''
        Computes the maximum card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return max(array)
        else:
            return None

    def max_health(self) -> Optional[int]:
        '''
        Computes the maximum card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return max(array)
        else:
            return None

    def max_intelligence(self) -> Optional[int]:
        '''
        Computes the maximum card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return max(array)
        else:
            return None

    def max_pitch(self) -> Optional[int]:
        '''
        Computes the maximum card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return max(array)
        else:
            return None

    def max_power(self) -> Optional[int]:
        '''
        Computes the maximum card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return max(array)
        else:
            return None

    def mean_cost(self) -> Optional[float]:
        '''
        Computes the mean card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return mean(array)
        else:
            return None

    def mean_defense(self) -> Optional[float]:
        '''
        Computes the mean card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return mean(array)
        else:
            return None

    def mean_health(self) -> Optional[float]:
        '''
        Computes the mean card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return mean(array)
        else:
            return None

    def mean_intelligence(self) -> Optional[float]:
        '''
        Computes the mean card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return mean(array)
        else:
            return None

    def mean_pitch(self) -> Optional[float]:
        '''
        Computes the mean card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return mean(array)
        else:
            return None

    def mean_power(self) -> Optional[float]:
        '''
        Computes the mean card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return mean(array)
        else:
            return None

    def median_cost(self) -> Optional[float]:
        '''
        Computes the median card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return median(array)
        else:
            return None

    def median_defense(self) -> Optional[float]:
        '''
        Computes the median card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return median(array)
        else:
            return None

    def median_health(self) -> Optional[float]:
        '''
        Computes the median card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return median(array)
        else:
            return None

    def median_intelligence(self) -> Optional[float]:
        '''
        Computes the median card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return median(array)
        else:
            return None

    def median_pitch(self) -> Optional[float]:
        '''
        Computes the median card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return median(array)
        else:
            return None

    def median_power(self) -> Optional[float]:
        '''
        Computes the median card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return median(array)
        else:
            return None

    def min_cost(self) -> Optional[int]:
        '''
        Computes the minimum card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return min(array)
        else:
            return None

    def min_defense(self) -> Optional[int]:
        '''
        Computes the minimum card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return min(array)
        else:
            return None

    def min_health(self) -> Optional[int]:
        '''
        Computes the minimum card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return min(array)
        else:
            return None

    def min_intelligence(self) -> Optional[int]:
        '''
        Computes the minimum card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return min(array)
        else:
            return None

    def min_pitch(self) -> Optional[int]:
        '''
        Computes the minimum card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return min(array)
        else:
            return None

    def min_power(self) -> Optional[int]:
        '''
        Computes the minimum card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return min(array)
        else:
            return None

    def save(self, file_path: str):
        '''
        Saves the list of cards to the specified file path.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            else:
                raise Exception('specified file path is not a JSON file')

    def statistics(self) -> dict[str, Optional[int | float]]:
        '''
        Computes helpful statistics associated with this collection of cards.
        The result is a dictionary containing the following keys:
        * count
        * max_[cost, defense, health, intelligence, pitch, power]
        * mean_[cost, defense, health, intelligence, pitch, power]
        * median_[cost, defense, health, intelligence, pitch, power]
        * min_[cost, defense, health, intelligence, pitch, power]
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
            'mean_cost': self.mean_cost(),
            'mean_defense': self.mean_defense(),
            'mean_health': self.mean_health(),
            'mean_intelligence': self.mean_intelligence(),
            'mean_pitch': self.mean_pitch(),
            'mean_power': self.mean_power(),
            'median_cost': self.median_cost(),
            'median_defense': self.median_defense(),
            'median_health': self.median_health(),
            'median_intelligence': self.median_intelligence(),
            'median_pitch': self.median_pitch(),
            'median_power': self.median_power(),
            'min_cost': self.min_cost(),
            'min_defense': self.min_defense(),
            'min_health': self.min_health(),
            'min_intelligence': self.min_intelligence(),
            'min_pitch': self.min_pitch(),
            'min_power': self.min_power(),
            'stdev_cost': self.stdev_cost(),
            'stdev_defense': self.stdev_defense(),
            'stdev_health': self.stdev_health(),
            'stdev_intelligence': self.stdev_intelligence(),
            'stdev_pitch': self.stdev_pitch(),
            'stdev_power': self.stdev_power(),
            'total_cost': self.total_cost(),
            'total_defense': self.total_defense(),
            'total_health': self.total_health(),
            'total_intelligence': self.total_intelligence(),
            'total_pitch': self.total_pitch(),
            'total_power': self.total_power(),
        }

    def stdev_cost(self) -> Optional[float]:
        '''
        Computes the standard deviation of card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return stdev(array)
        else:
            return None

    def stdev_defense(self) -> Optional[float]:
        '''
        Computes the standard deviation of card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return stdev(array)
        else:
            return None

    def stdev_health(self) -> Optional[float]:
        '''
        Computes the standard deviation of card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return stdev(array)
        else:
            return None

    def stdev_intelligence(self) -> Optional[float]:
        '''
        Computes the standard deviation of card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return stdev(array)
        else:
            return None

    def stdev_pitch(self) -> Optional[float]:
        '''
        Computes the standard deviation of card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return stdev(array)
        else:
            return None

    def stdev_power(self) -> Optional[float]:
        '''
        Computes the standard deviation of card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return stdev(array)
        else:
            return None

    def to_json(self) -> str:
        '''
        Converts the list of cards to a JSON string representation.
        '''
        return json.dumps([card.to_dict() for card in self.items])

    def total_cost(self) -> Optional[int]:
        '''
        Computes the total card cost within this card list. Cards with
        variable or no cost are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.cost for x in self if isinstance(x.cost, int)]
        if array:
            return sum(array)
        else:
            return None

    def total_defense(self) -> Optional[int]:
        '''
        Computes the total card defense within this card list. Cards with
        variable or no defense are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.defense for x in self if isinstance(x.defense, int)]
        if array:
            return sum(array)
        else:
            return None

    def total_health(self) -> Optional[int]:
        '''
        Computes the total card health within this card list. Cards with
        variable or no health are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return sum(array)
        else:
            return None

    def total_intelligence(self) -> Optional[int]:
        '''
        Computes the total card intelligence within this card list. Cards with
        variable or no intelligence are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.intelligence for x in self if isinstance(x.intelligence, int)]
        if array:
            return sum(array)
        else:
            return None

    def total_pitch(self) -> Optional[int]:
        '''
        Computes the total card pitch within this card list. Cards with
        variable or no pitch are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.pitch for x in self if isinstance(x.pitch, int)]
        if array:
            return sum(array)
        else:
            return None

    def total_power(self) -> Optional[int]:
        '''
        Computes the total card power within this card list. Cards with
        variable or no power are ignored.
        '''
        if len(self.items) < 1: return None
        array = [x.power for x in self if isinstance(x.power, int)]
        if array:
            return sum(array)
        else:
            return None
