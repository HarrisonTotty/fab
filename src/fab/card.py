'''
Contains the definitions of Flesh and Blood cards and card lists.
'''

from __future__ import annotations

import csv
import copy
import dataclasses
import io
import json
import os
import random

from collections import UserList
from IPython.display import display, Image, Markdown
from pandas import DataFrame, Series
from statistics import mean, median, stdev
from typing import Any, Optional
from unidecode import unidecode

from .meta import GAME_FORMATS, ICON_CODE_IMAGE_URLS, RARITIES

CARD_CATALOG: Optional[CardList] = None

JSON_INDENT: Optional[int] = 2

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

TCGPLAYER_BASE_URL = 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q='

@dataclasses.dataclass
class Card:
    '''
    Represents a Flesh and Blood card.

    Note:
      `fab` treats all prints and versions of a card as under the same `Card`
      object. If any change is made to the card's body text or attributes
      between prints, it can be assumed that `fab` lists the latest print of the
      card.

    Attributes:
      body: The full body text of the card, excluding flavor text.
      cost: The resource cost of the card.
      defense: The defense value of the card.
      flavor_text: Any lore text printed on the body of the card.
      full_name: The full name of the card, including pitch value.
      grants: A list of keywords this card grants to other cards.
      health: The health value of the card.
      identifiers: The list of card identifiers, such as `RNR012`.
      image_urls: A list of card image URLs.
      intelligence: The intelligence value of the card.
      keywords: A list of keywords associated with the card, such as `Dominate`.
      legality: Whether this card is _currently_ legal for various formats (see `meta.GAME_FORMATS`).
      name: The name of the card, excluding pitch value.
      pitch: The pitch value of the card.
      power: The (attack) power of the card.
      rarities: The list of rarities associated with each card identifier.
      sets: The list of card set codes associated with the card.
      tags: A collection of user-defined tags.
      type_text: The full type box text of the card.
      types: The list of types present in the card's type box.
    '''

    body: Optional[str]
    cost: int | str | None
    defense: int | str | None
    flavor_text: Optional[str]
    full_name: str
    grants: list[str]
    health: Optional[int]
    identifiers: list[str]
    image_urls: list[str]
    intelligence: Optional[int]
    keywords: list[str]
    legality: dict[str, bool]
    name: str
    pitch: Optional[int]
    power: int | str | None
    rarities: list[str]
    sets: list[str]
    tags: list[str]
    type_text: str
    types: list[str]

    def __getitem__(self, key: str) -> Any:
        '''
        Allows one to access fields of a card via dictionary syntax.

        Args:
          key: The name of the class attribute to fetch.

        Returns:
          The value associated with the specified field.
        '''
        return self.__dict__[key]

    def __hash__(self) -> Any:
        '''
        Computes the hash representation of the card.

        Returns:
          The hash representation of the card.
        '''
        return hash((self.name, self.pitch, self.type_text))

    def __str__(self) -> str:
        '''
        Computes the JSON string representation of the card.

        This is an alias of the `to_json()` method.

        Returns:
          The JSON string representation of the card.
        '''
        return self.to_json()

    @staticmethod
    def from_full_name(full_name: str, catalog: Optional[CardList] = None) -> Card:
        '''
        Creates a new card from its full name.

        Note:
          To instantiate the card this way, a card catalog (`CardList`) must be
          provided, defaulting to `card.CARD_CATALOG`.

        Args:
          full_name: The full name of the card (including pitch value, if applicable).
          catalog: The card catalog to use as a reference, defaulting to `card.CARD_CATALOG` if `None`.

        Returns:
          A new `Card` object.
        '''
        _catalog = CARD_CATALOG if catalog is None else catalog
        if _catalog is None: raise Exception('specified card catalog has not been initialized')
        grouped = _catalog.group(by='full_name')
        if not full_name in grouped:
            raise Exception(f'specified card catalog does not contain a card will full name "{full_name}"')
        return copy.deepcopy(grouped[full_name][0])

    @staticmethod
    def from_identifier(identifier: str, catalog: Optional[CardList] = None) -> Card:
        '''
        Creates a new card from its identifier.

        Note:
          To instantiate the card this way, a card catalog (`CardList`) must be
          provided, defaulting to `card.CARD_CATALOG`.

        Args:
          identifier: The identifier of the card.
          catalog: The card catalog to use as a reference, defaulting to `card.CARD_CATALOG` if `None`.

        Returns:
          A new `Card` object.
        '''
        _catalog = CARD_CATALOG if catalog is None else catalog
        if _catalog is None: raise Exception('specified card catalog has not been initialized')
        for card in _catalog:
            if identifier in card.identifiers:
                return copy.deepcopy(card)
        raise Exception(f'no card in catalog found with identifier "{identifier}"')

    @staticmethod
    def from_json(jsonstr: str) -> Card:
        '''
        Creates a new card from the specified JSON string.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `Card` object.
        '''
        return Card(**json.loads(jsonstr))

    def image(self, height: int = 314, index: int = -1, width: int = 225) -> Any:
        '''
        Display an image of this card, optionally providing an alternative
        index to use.

        Args:
          height: The height to scale the resulting image to, in pixels.
          index: The target `image_urls` index to fetch image data for.
          width: The width to scale the resulting image to, in pixels.

        Returns:
          The image representation of the card.
        '''
        if not self.image_urls: return 'No images available'
        return display(Image(self.image_urls[index], height=height, width=width))

    def is_action(self) -> bool:
        '''
        Whether this card is an action card.

        Returns:
          Whether the card contains the _Action_ type.
        '''
        return 'Action' in self.types

    def is_attack(self) -> bool:
        '''
        Whether this card is an attack card.

        Returns:
          Whether the card contains the _Attack_ type.
        '''
        return 'Attack' in self.types

    def is_attack_reaction(self) -> bool:
        '''
        Whether this card is an attack reaction card.

        Returns:
          Whether the card contains the _Attack Reaction_ type.
        '''
        return 'Attack Reaction' in self.types

    def is_aura(self) -> bool:
        '''
        Whether this card is an aura card.

        Returns:
          Whether the card contains the _Aura_ type.
        '''
        return 'Aura' in self.types

    def is_blue(self) -> bool:
        '''
        Whether this is a blue card.

        Returns:
          Whether this card pitches for 3 resources.
        '''
        return self.pitch == 3 if isinstance(self.pitch, int) else False

    def is_defense_reaction(self) -> bool:
        '''
        Whether this card is a defense reaction card.

        Returns:
          Whether the card contains the _Defense Reaction_ type.
        '''
        return 'Defense Reaction' in self.types

    def is_equipment(self) -> bool:
        '''
        Whether this card is an equipment card.

        Returns:
          Whether the card contains the _Equipment_ type.
        '''
        return 'Equipment' in self.types

    def is_hero(self) -> bool:
        '''
        Whether this card is a hero card.

        Returns:
          Whether the card contains the _Hero_ type.
        '''
        return 'Hero' in self.types

    def is_instant(self) -> bool:
        '''
        Whether this card is an instant card.

        Returns:
          Whether the card contains the _Instant_ type.
        '''
        return 'Instant' in self.types

    def is_item(self) -> bool:
        '''
        Whether this card is an item card.

        Returns:
          Whether the card contains the _Item_ type.
        '''
        return 'Item' in self.types

    def is_legal(self, format: Optional[str] = None) -> bool:
        '''
        Whether this card is legal for the specified format, or if `format` is
        `None`, returns `False` if this card is banned in _any_ format.

        Args:
          format: The code of the card format to check, or `None` to check all formats.

        Returns:
          Whether the card is legal.
        '''
        if not self.legality: return True
        if format is None:
            return False in self.legality.values()
        else:
            return self.legality[format]

    def is_reaction(self) -> bool:
        '''
        Whether this card is an attack or defense reaction card.

        Returns:
          Whether the card contains the _Attack Reaction_ or _Defense Reaction_ types.
        '''
        return self.is_attack_reaction() or self.is_defense_reaction()

    def is_red(self) -> bool:
        '''
        Whether this is a red card.

        Returns:
          Whether this card pitches for 1 resource.
        '''
        return self.pitch == 1 if isinstance(self.pitch, int) else False

    def is_token(self) -> bool:
        '''
        Whether this card is a token card.

        Returns:
          Whether the card contains the _Token_ type.
        '''
        return 'Token' in self.types

    def is_weapon(self) -> bool:
        '''
        Whether this card is a weapon card.

        Returns:
          Whether the card contains the _Weapon_ type.
        '''
        return 'Weapon' in self.types

    def is_yellow(self) -> bool:
        '''
        Whether this is a yellow card.

        Returns:
          Whether this card pitches for 2 resources.
        '''
        return self.pitch == 2 if isinstance(self.pitch, int) else False

    def keys(self) -> list[str]:
        '''
        Returns the dictionary keys associated with this card class.

        Returns:
          The `dict` keys as `list[str]`, corresponding to the possible fields of the card.
        '''
        return list(self.__dict__.keys())

    def rarity_names(self) -> list[str]:
        '''
        Returns the full names of the rarities associated with this card.

        Returns:
          A `list` of card rarity names associated with the card.
        '''
        return [RARITIES[r] for r in self.rarities]

    def render(self, heading_level: str = '###', icon_size: int = 11) -> Any:
        '''
        Renders this card into a markdown representation.

        Args:
          heading_level: Specifies the initial heading level of the card.
          icon_size: Specified the target width of icon images.

        Returns:
          The IPython-rendered markdown output.
        '''
        mdstr = f'{heading_level} {self.name} _({self.type_text})_\n\n'
        if not self.body is None:
            with_images = self.body
            for k, v in ICON_CODE_IMAGE_URLS.items():
                with_images = with_images.replace(k, f'<img src="{v}" alt="{k}" width="{icon_size}"/>')
            mdstr += f'{with_images}\n\n'
        if not self.flavor_text is None:
            mdstr += f'{self.flavor_text}\n\n'
        mdstr += '| Attribute | Value |\n|---|---|\n'
        if not self.power is None:
            mdstr += f'| Attack Power | {self.power} |\n'
        if not self.defense is None:
            mdstr += f'| Defense | {self.defense} |\n'
        if not self.health is None:
            mdstr += f'| Health | {self.health} |\n'
        if not self.intelligence is None:
            mdstr += f'| Intelligence | {self.intelligence} |\n'
        if not self.pitch is None:
            mdstr += f'| Pitch Value | {self.pitch} |\n'
        if not self.cost is None:
            mdstr += f'| Resource Cost | {self.cost} |\n'
        return display(Markdown(mdstr))

    def render_body(self, icon_size: int = 11) -> Any:
        '''
        Renders the body text of this card as markdown output.

        Args:
          icon_size: Specified the target width of icon images.

        Returns:
          The IPython-rendered markdown output.
        '''
        if self.body is None: return 'Specified card does not have any body text.'
        with_images = self.body
        for k, v in ICON_CODE_IMAGE_URLS.items():
            with_images = with_images.replace(k, f'<img src="{v}" alt="{k}" width="{icon_size}"/>')
        return display(Markdown(with_images))

    def tcgplayer_url(self) -> str:
        '''
        Computes the [TCG Player](https://www.tcgplayer.com/) URL for the card.

        Returns:
          The URL used to search for the card on TCG Player.
        '''
        return TCGPLAYER_BASE_URL + self.name

    def to_dict(self) -> dict[str, Any]:
        '''
        Converts this card into a raw python dictionary.

        Returns:
          A copy of the raw `dict` representation of the card.
        '''
        return copy.deepcopy(self.__dict__)

    def to_json(self) -> str:
        '''
        Computes the card's JSON string representation.

        Returns:
          A JSON string representation of the card.
        '''
        return json.dumps(self.__dict__, indent=JSON_INDENT)

    def to_series(self) -> Series:
        '''
        Converts the card into a [pandas Series
        object](https://pandas.pydata.org/docs/reference/series.html).

        Returns:
          A pandas `Series` object associated with the card.
        '''
        return Series(self.to_dict())


class CardList(UserList):
    '''
    Represents a collection of cards.

    Note:
      This is ultimately a superclass of `list`, and thus supports all common
      `list` methods.

    Attributes:
      data: The raw `list` of `Card` objects contained within the object.
    '''
    data: list[Card]

    def actions(self) -> CardList:
        '''
        Returns the set of all action cards in this card list.

        Returns:
          The set of all action cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_action()])

    def attacks(self) -> CardList:
        '''
        Returns the set of all attack cards in this card list.

        Returns:
          The set of all attack cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_attack()])

    def attack_reactions(self) -> CardList:
        '''
        Returns the set of all attack reaction cards in this card list.

        Returns:
          The set of all attack reaction cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_attack_reaction()])

    def auras(self) -> CardList:
        '''
        Returns the set of all aura cards in this card list.

        Returns:
          The set of all aura cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_aura()])

    def costs(self) -> list[int]:
        '''
        Returns the set of all card costs associated with this list of cards.

        Tip: Warning
          This excludes cards with no cost or with variable cost.

        Returns:
          The set of all card costs in the card list.
        '''
        res = []
        for card in self.data:
            if isinstance(card.cost, int): res.append(card.cost)
        return sorted(list(set(res)))

    def counts(self) -> dict[str, int]:
        '''
        Computes a `dict` of card counts, where keys correspond to the
        `full_name` of `Card` objects.

        Returns:
          A `dict` of card counts by full name.
        '''
        counts = {}
        for card in self.data:
            if card.full_name in counts:
                counts[card.full_name] += 1
            else:
                counts[card.full_name] = 1
        return counts

    def defense_reactions(self) -> CardList:
        '''
        Returns the set of all defense reaction cards in this card list.

        Returns:
          The set of all defense reaction cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_defense_reaction()])

    def defense_values(self) -> list[int]:
        '''
        Returns the set of all card defense values associated with this list of
        cards.

        Tip: Warning
          This excludes cards with no defense or with variable defense.

        Returns:
          A unique `list` of card defense values associated with the list of cards.
        '''
        res = []
        for card in self.data:
            if isinstance(card.defense, int): res.append(card.defense)
        return sorted(list(set(res)))

    def draw(self, num: int, order: int = -1, remove: bool = False) -> CardList:
        '''
        Draws the specified number of cards from the list, optionally removing
        the cards drawn.

        Note:
          If `order` is set to `-1`, then cards will be drawn from the _end_ of
          the list, as if calling `list.pop()`. When `order` is `1`, cards are
          drawn from the beginning of the list. If `order` is `0`, then cards
          are drawn from random positions. Even when `remove` is `False`, when
          drawing with `order=0`, this method will ensure that the same card
          will not be drawn more times than it actually exists in the list.

        Args:
          num: The number of cards to draw from the list.
          order: Specifies the method/order in which cards are drawn from the list (see note).
          remove: Whether to remove the cards drawn from the list.

        Returns:
          The list of cards drawn.
        '''
        if num <= 0:
            raise Exception('specified number of cards must be a positive integer')
        res = []
        if order == -1:
            if remove:
                for _ in range(0, num):
                    res.append(self.pop())
            else:
                res = self.data[-num:]
        elif order == 0:
            if remove:
                for _ in range(0, num):
                    res.append(self.pop(random.randrange(len(self.data))))
            else:
                potential = [c for c in self.data]
                for _ in range(0, num):
                    res.append(potential.pop(random.randrange(len(potential))))
        elif order == 1:
            if remove:
                for _ in range(0, num):
                    res.append(self.pop(0))
            else:
                res = self.data[num:]
        else:
            raise Exception('specified "order" must be -1, 0, or 1')
        return CardList(res)

    @staticmethod
    def empty() -> CardList:
        '''
        Returns a new empty card list containing no cards.

        Returns:
          An empty card list.
        '''
        return CardList([])

    def equipment(self) -> CardList:
        '''
        Returns the set of all equipment cards in this card list.

        Returns:
          The set of all equipment cards in the card list.
        '''
        return CardList([card for card in self.data if card.is_equipment()])

    def filter(
            self,
            body: Optional[Any] = None,
            cost: Optional[Any] = None,
            defense: Optional[Any] = None,
            full_name: Optional[Any] = None,
            grants: Optional[Any] = None,
            health: Optional[Any] = None,
            intelligence: Optional[Any] = None,
            keywords: Optional[Any] = None,
            legality: Optional[Any] = None,
            name: Optional[Any] = None,
            negate: bool = False,
            pitch: Optional[Any] = None,
            power: Optional[Any] = None,
            rarities: Optional[Any] = None,
            sets: Optional[Any] = None,
            tags: Optional[Any] = None,
            type_text: Optional[Any] = None,
            types: Optional[Any] = None
    ) -> CardList:
        '''
        Filters a list of cards according to a function against a particular
        `Card` field.

        In addition to functions/lambdas, you can also specify:

        * A `str` for the `body`, `full_name`, `name`, or `type_text` keyword
          arguments. These comparisons are case-insensitive and will match
          substrings.
        * An `int` for the `cost`, `defense`, `health`, `intelligence`,
          `pitch`, or `power` keyword arguments. `None` and `str` values
          will not be included in the results.
        * A `tuple[int, int]` for the `cost`, `defense`, `health`,
          `intelligence`, `pitch`, or `power` keyword arguments. This defines
          a range of values to include (inclusive).
        * A `list[str]` for the `grants`, `keywords`, `rarities`, `sets`,
          `tags`, and `types` keyword arguments. At least one value of the
          list must be present for an item to be included.
        * A `str` for the `grants`, `keywords`, `rarities`, `sets`, `tags`,
          and `types` keyword arguments. This is the same as passing in a
          single-element list.
        * A `str` for the `legality` keyword argument, corresponding to a format
          code that the card must be legal in to be included.
        * The strings `r`, `red`, `y`, `yellow`, `b`, or `blue` for the `pitch`
          keyword argument, corresponding to the color of the card
          (case-insensitive).

        Args:
          body: A `str` or function to filter by `body`.
          cost: An `int`, `tuple[int, int]`, or function to filter by `cost`.
          defense: An `int`, `tuple[int, int]`, or function to filter by `defense`.
          full_name: A `str` or function to filter by `full_name`.
          grants: A `str`, `list[str]`, or function to filter by `grants`.
          health: An `int`, `tuple[int, int]`, or function to filter by `health`.
          intelligence: An `int`, `tuple[int, int]`, or function to filter by `intelligence`.
          keywords: A `str`, `list[str]`, or function to filter by `keywords`.
          legality: A `str` or function to filter by `legality`.
          name: A `str` or function to filter by `name`.
          negate: Whether to invert the filter specification.
          pitch: An `int`, `str`, `tuple[int, int]`, or function to filter by `pitch`.
          power: An `int`, `tuple[int, int]`, or function to filter by `power`.
          rarities: A `str`, `list[str]` or function to filter by `rarities`.
          sets: A `str`, `list[str]`, or function to filter by `sets`.
          tags: A `str`, `list[str]`, or function to filter by `tags`.
          type_text: A `str` or function to filter by `type_text`.
          types: A `str`, `list[str]`, or function to filter by `types`.

        Returns:
          A new `CardList` containing copies of `Card` objects that meet the filtering requirements.
        '''
        if len(self.data) < 2: return copy.deepcopy(self)
        filtered = []
        for c in self:
            if not body is None:
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
            if not cost is None:
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
            if not defense is None:
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
            if not full_name is None:
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
            if not grants is None:
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
            if not health is None:
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
            if not intelligence is None:
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
            if not keywords is None:
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
            if not legality is None:
                if isinstance(legality, str):
                    if negate:
                        if c.legality[legality]: continue
                    else:
                        if not c.legality[legality]: continue
                else:
                    if negate:
                        if legality(c.legality): continue
                    else:
                        if not legality(c.legality): continue
            if not name is None:
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
            if not pitch is None:
                if isinstance(pitch, int):
                    if negate:
                        if isinstance(c.pitch, int) and pitch == c.pitch: continue
                    else:
                        if not isinstance(c.pitch, int) or pitch != c.pitch: continue
                elif isinstance(pitch, str):
                    pl = pitch.lower()
                    if not pl in ['r', 'red', 'y', 'yellow', 'b', 'blue']:
                        raise Exception(f'unknown pitch filter string "{pitch}"')
                    if negate:
                        if pl.startswith('b') and c.is_blue(): continue
                        elif pl.startswith('r') and c.is_red(): continue
                        elif pl.startswith('y') and c.is_yellow(): continue
                    else:
                        if pl.startswith('b') and not c.is_blue(): continue
                        elif pl.startswith('r') and not c.is_red(): continue
                        elif pl.startswith('y') and not c.is_yellow(): continue
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
            if not power is None:
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
            if not rarities is None:
                if isinstance(rarities, str):
                    if negate:
                        if rarities in c.rarities: continue
                    else:
                        if not rarities in c.rarities: continue
                elif isinstance(rarities, list):
                    if negate:
                        if True in [(x in c.rarities) for x in rarities]: continue
                    else:
                        if not (True in [(x in c.rarities) for x in rarities]): continue
                else:
                    if negate:
                        if rarities(c.rarities): continue
                    else:
                        if not rarities(c.rarities): continue
            if not sets is None:
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
            if not tags is None:
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
            if not type_text is None:
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
            if not types is None:
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

        Args:
          csvstr: The CSV string representation to parse.
          delimiter: An alternative primary delimiter to pass to `csv.DictReader`.

        Returns:
          A new `CardList` object from the parsed data.
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
        def image_url_parser(inputstr: str) -> list[str]:
            '''
            A helper function for parsing our the image URL list.
            '''
            if not inputstr: return []
            result = []
            if ',' in inputstr:
                for substrings in [x.split(' - ', 1) for x in unidecode(inputstr).split(',') if ' - ' in x]:
                    url = substrings[0].strip()
                    result.append(url)
            elif ' - ' in inputstr:
                url = unidecode(inputstr).split(' - ', 1)[0].strip()
                result.append(url)
            return result
        def legality_parser(csv_entry: dict[str, Any]) -> dict[str, bool]:
            '''
            A helper function for parsing card legality.
            '''
            res = {}
            blitz_legal = not csv_entry['Blitz Legal'].lower() in ['no', 'false']
            blitz_ll = True if csv_entry['Blitz Living Legend'] else False
            blitz_banned = True if csv_entry['Blitz Banned'] else False
            cc_legal = not csv_entry['CC Legal'].lower() in ['no', 'false']
            cc_ll = True if csv_entry['CC Living Legend'] else False
            cc_banned = True if csv_entry['CC Banned'] else False
            commoner_legal = not csv_entry['Commoner Legal'].lower() in ['no', 'false']
            commoner_banned = True if csv_entry['Commoner Banned'] else False
            res['B'] = blitz_legal and not blitz_ll and not blitz_banned
            res['CC'] = cc_legal and not cc_ll and not cc_banned
            res['C'] = commoner_legal and not commoner_banned
            res['UPF'] = res['CC']
            return res
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
                  legality     = legality_parser(entry),
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

        Args:
          jsonstr: The JSON string representation to parse into a card list.

        Returns:
          A new `CardList` object from the parsed data.
        '''
        cards = []
        for jcard in json.loads(jsonstr):
            cards.append(Card(**jcard))
        return CardList(cards)

    def full_names(self) -> list[str]:
        '''
        Returns the set of all full card names within this list of cards.

        Returns:
          A unique `list` of all full card names within the list of cards.
        '''
        return sorted(list(set([card.full_name for card in self.data])))

    def grants(self) -> list[str]:
        '''
        Returns the set of all card grant keywords within this list of cards.

        Returns:
          A unique `list` of all card grant keywords within the list of cards.
        '''
        res = []
        for card in self.data:
            res.extend(card.grants)
        return sorted(list(set(res)))

    def group(self, by: str = 'type_text') -> dict[int | str, CardList]:
        '''
        Groups cards by the specified (singular form) of the `Card` field.

        Note:
          The keys of the resulting `dict` take on the `type` described below:

          * `str`: `full_name`, `grants`, `keyword`, `name`, `rarity`, `set`, `type`, `type_text`
          * `int`: `cost`, `defense`, `health`, `intelligence`, `pitch`, `power`

          Certain values of `by` accept their plural forms, such as `rarity` or
          `rarities`.

        Tip: Warning
          When grouping by `cost`, `defense`, `health`, `intelligence`, `pitch`,
          or `power`, cards with `str` or `None` values for the corresponding
          field will be excluded from the result.

        Args:
          by: The `Card` field to group by.

        Returns:
          A `dict` of `CardList` objects grouped by the specified `Card` field.
        '''
        if len(self.data) < 1: return {}
        res = {}
        # str keys
        if by == 'full_name':
            for full_name in self.full_names():
                res[full_name] = CardList([card for card in self if card.full_name == full_name]).sort()
        elif by == 'grants':
            for grants in self.grants():
                res[grants] = CardList([card for card in self if grants in card.grants]).sort()
        elif by in ['keyword', 'keywords']:
            for keyword in self.keywords():
                res[keyword] = CardList([card for card in self if keyword in card.keywords]).sort()
        elif by == 'name':
            for name in self.names():
                res[name] = CardList([card for card in self if card.name == name]).sort()
        elif by in ['rarity', 'rarities']:
            for rarity in self.rarities():
                res[rarity] = CardList([card for card in self if rarity in card.rarities]).sort()
        elif by in ['set', 'sets']:
            for card_set in self.sets():
                res[card_set] = CardList([card for card in self if card_set in card.sets]).sort()
        elif by in ['type', 'types']:
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
        cards.

        Tip: Warning
          This excludes cards with no health or with variable health.

        Returns:
          The unique `list` of all card health values within the card list.
        '''
        res = []
        for card in self.data:
            if isinstance(card.health, int): res.append(card.health)
        return sorted(list(set(res)))

    @staticmethod
    def _hero_filter_related(hero: Card, cards: CardList, catalog: Optional[CardList] = None, include_generic: bool = True) -> CardList:
        '''
        A helper function for filtering cards based on a hero. Do not call this
        function directly, instead use `Deck.filter_related`.

        Note:
          This function needs a card catalog to work properly and will fall back
          to `card.CARD_CATALOG`.

        Args:
          hero: The hero card to filter with.
          cards: The collection of cards to filter.
          catalog: A catalog of cards representing all cards in the game.
          include_generic: Whether to include _Generic_ cards in the result.

        Returns:
          The list of cards that work with the specified hero.
        '''
        _catalog = CARD_CATALOG if catalog is None else catalog
        if _catalog is None:
            raise Exception('specified card catalog (or default card catalog) has not been initialized')
        if 'Shapeshifter' in hero.types: return cards
        other_hero_types = _catalog.filter(types='Hero').filter(full_name=hero.name, negate=True).types()
        relevant = [t for t in other_hero_types if not t in hero.types]
        filtered = cards.filter(
            types = [t for t in hero.types if not t in ['Hero', 'Young']] + (['Generic'] if include_generic else [])
        ).filter(
            types = lambda card_types: not any(t in relevant for t in card_types)
        )
        final = []
        for card in filtered.data:
            if any('Specialization' in k for k in card.keywords):
                spec = next(k for k in card.keywords if 'Specialization' in k).replace('Specialization', '').strip()
                if spec.lower() in hero.full_name.lower():
                    final.append(card)
            else:
                final.append(card)
        return CardList(copy.deepcopy(final))

    def heroes(self) -> CardList:
        '''
        Returns the set of all hero cards in this card list.

        Returns:
          The set of all hero cards within the card list.
        '''
        return CardList([card for card in self.data if card.is_hero()])

    def identifiers(self) -> list[str]:
        '''
        Returns the set of all card identifiers in this card list.

        Returns:
          The unique `list` of all card identifiers within the card list.
        '''
        res = []
        for card in self.data:
            res.extend(card.identifiers)
        return sorted(list(set(res)))

    def instants(self) -> CardList:
        '''
        Returns the set of all instant cards in this card list.

        Returns:
          The set of all instant cards within the card list.
        '''
        return CardList([card for card in self.data if card.is_instant()])

    def intelligence_values(self) -> list[int]:
        '''
        Returns the set of all card intelligence values associated with this
        list of cards.

        Tip: Warning
          This excludes cards with no intelligence or with variable
          intelligence.

        Returns:
          A unique `list` of all card intelligence values within the list of cards.
        '''
        res = []
        for card in self.data:
            if isinstance(card.intelligence, int): res.append(card.intelligence)
        return sorted(list(set(res)))

    def item_cards(self) -> CardList:
        '''
        Returns the set of all item cards in this card list.

        Returns:
          The set of all item cards within the list of cards.
        '''
        return CardList([card for card in self.data if card.is_item()])

    def keywords(self) -> list[str]:
        '''
        Returns the set of all keywords in this card list.

        Returns:
          A unique `list` of all keywords within the list of cards.
        '''
        res = []
        for card in self.data:
            res.extend(card.keywords)
        return sorted(list(set(res)))

    def legality(self) -> dict[str, bool]:
        '''
        Computes the legality of this list of cards for each game format.

        Note:
          A `CardList` is not considered legal for a format if it contains _any_
          cards not legal for that format.

        Returns:
          A `dict` of game format `str` keys and their `bool` legal status.
        '''
        res = {}
        for f in GAME_FORMATS.keys():
            res[f] = not (False in [card.is_legal(f) for card in self.data])
        return res

    @staticmethod
    def load(file_path: str, set_catalog: bool = False) -> CardList:
        '''
        Loads a list of cards from the specified `.json` or `.csv` file.

        Note:
          If `set_catalog` is set to `True`, then a copy of the loaded card list
          will also be set as the default `card.CARD_CATALOG`.

        Args:
          file_path: The file path to load from.
          set_catalog: Whether to also set the loaded data as the default card catalog.

        Returns:
          A new `CardList` object.
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
        Computes the maximum card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Returns:
          The maximum card cost within the list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_defense(self) -> int:
        '''
        Computes the maximum card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Returns:
          The maximum card defense value within the list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_health(self) -> int:
        '''
        Computes the maximum card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Returns:
          The maximum card health value within the list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.health for x in self.data if isinstance(x.health, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_intelligence(self) -> int:
        '''
        Computes the maximum card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Returns:
          The maximum card intelligence value within the list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_pitch(self) -> int:
        '''
        Computes the maximum card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Returns:
          The maximum card pitch value within this list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if array:
            return max(array)
        else:
            return 0

    def max_power(self) -> int:
        '''
        Computes the maximum card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Returns:
          The maximum card power value within this list of cards.
        '''
        if len(self.data) < 1: return 0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if array:
            return max(array)
        else:
            return 0

    def mean_cost(self, precision: int = 2) -> float:
        '''
        Computes the mean card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean card cost of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_defense(self, precision: int = 2) -> float:
        '''
        Computes the mean card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean defense of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_health(self, precision: int = 2) -> float:
        '''
        Computes the mean card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean health of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.health for x in self.data if isinstance(x.health, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the mean card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean intelligence of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_pitch(self, precision: int = 2) -> float:
        '''
        Computes the mean card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean pitch value of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def mean_power(self, precision: int = 2) -> float:
        '''
        Computes the mean card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean power of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if array:
            return round(mean(array), precision)
        else:
            return 0.0

    def median_cost(self, precision: int = 2) -> float:
        '''
        Computes the median card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median resource cost of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_defense(self, precision: int = 2) -> float:
        '''
        Computes the median card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median defense value of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_health(self, precision: int = 2) -> float:
        '''
        Computes the median card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median health of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.health for x in self if isinstance(x.health, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the median card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median intelligence of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_pitch(self, precision: int = 2) -> float:
        '''
        Computes the median card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median pitch vlaue of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    def median_power(self, precision: int = 2) -> float:
        '''
        Computes the median card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median attack power of cards in the list.
        '''
        if len(self.data) < 1: return 0.0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if array:
            return round(median(array), precision)
        else:
            return 0.0

    @staticmethod
    def merge(*args: CardList, unique: bool = False) -> CardList:
        '''
        Merges two or more card lists into a single one.

        Args:
          *args: The `CardList` objects to merge.
          unique: Whether duplicate `Card` objects should be deleted.

        Returns:
          The merged collection of cards.
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
        Computes the minimum card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Returns:
          The minimum card cost within the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_defense(self) -> int:
        '''
        Computes the minimum card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Returns:
          The minimum card defense value within the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_health(self) -> int:
        '''
        Computes the minimum card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Returns:
          The minimum card health in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.health for x in self.data if isinstance(x.health, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_intelligence(self) -> int:
        '''
        Computes the minimum card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Returns:
          The minimum intelligence in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_pitch(self) -> int:
        '''
        Computes the minimum card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Returns:
          The minimum pitch value in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if array:
            return min(array)
        else:
            return 0

    def min_power(self) -> int:
        '''
        Computes the minimum card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Returns:
          The minimum attack power in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if array:
            return min(array)
        else:
            return 0

    def names(self) -> list[str]:
        '''
        Returns the set of all card names in this card list.

        Returns:
          The unique `list` of card names within the list of cards.
        '''
        return sorted(list(set([card.name for card in self.data])))

    def num_blue(self) -> int:
        '''
        Returns the number of "blue" cards (pitch 3) in this card list.

        Returns:
          The number of cards in this card list that pitch for 3 resources.
        '''
        return len(self.filter(pitch=3))

    def num_red(self) -> int:
        '''
        Returns the number of "red" cards (pitch 1) in this card list.

        Returns:
          The number of cards in this card list that pitch for 1 resource.
        '''
        return len(self.filter(pitch=1))

    def num_yellow(self) -> int:
        '''
        Returns the number of "yellow" cards (pitch 2) in this card list.

        Returns:
          The number of cards in this card list that pitch for 2 resources.
        '''
        return len(self.filter(pitch=2))

    def pitch_cost_difference(self) -> int:
        '''
        Returns the difference between the pitch and cost values of all cards.

        Note:
          A positive integer indicates that on average one generates more pitch
          value than consumes it.

        Tip: Warning
          This calculation does not take into effect any additional pitch/cost a
          card might incur in its body text.

        Returns:
          The pitch-cost difference of the list of cards.
        '''
        return self.total_pitch() - self.total_cost()

    def pitch_values(self) -> list[int]:
        '''
        Returns the set of all card pitch values associated with this list of
        cards.

        Tip: Warning
          This excludes cards with no pitch or with variable pitch.

        Returns:
          The unique `list` of card pitch values within the list of cards.
        '''
        res = []
        for card in self.data:
            if isinstance(card.pitch, int): res.append(card.pitch)
        return sorted(list(set(res)))

    def power_defense_difference(self) -> int:
        '''
        Returns the difference between the power and defense values of all
        cards.

        Note:
          A positive integer indicates the deck prefers an offensive strategy.

        Tip: Warning
          This calculation does not take into effect any additional power/defense
          a card might incur in its body text.

        Returns:
          The power-defense difference of the list of cards.
        '''
        return self.total_power() - self.total_defense()

    def power_values(self) -> list[int]:
        '''
        Returns the set of all card power values associated with this list of
        cards.

        Tip: Warning
          This excludes cards with no power or with variable power.

        Returns:
          The unique `list` of power values within the list of cards.
        '''
        res = []
        for card in self.data:
            if isinstance(card.power, int): res.append(card.power)
        return sorted(list(set(res)))

    def save(self, file_path: str):
        '''
        Saves the list of cards to the specified file path.

        Args:
          file_path: The file path to save to.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            else:
                raise Exception('specified file path is not a JSON file')

    def sort(self, key: Any = 'name', reverse: bool = False) -> CardList:
        '''
        Sorts the list of cards, returning a new sorted collection.

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

        Args:
          key: The `Card` field to sort by.
          reverse: Whether to reverse the sort order.

        Returns:
          A new, sorted `CardList` object.
        '''
        if isinstance(key, str):
            contains_none = []
            to_sort = []
            for card in self.data:
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
            return CardList(sorted(copy.deepcopy(self.data), key = key, reverse = reverse))

    def rarities(self) -> list[str]:
        '''
        Returns the set of all card rarities in this card list.

        Returns:
          A unique `list` of card rarities in the list of cards.
        '''
        res = []
        for card in self.data:
            res.extend(card.rarities)
        return sorted(list(set(res)))

    def reactions(self) -> CardList:
        '''
        Returns the set of all attack and defense reaction cards in this card
        list.

        Returns:
          A list of all attack and defense reaction cards within the card list.
        '''
        return CardList([card for card in self.data if card.is_reaction()])

    def sets(self) -> list[str]:
        '''
        Returns the set of all card sets in this list.

        Returns:
          A unique `list` of all card sets within the list of cards.
        '''
        card_sets = []
        for card in self.data:
            card_sets.extend(card.sets)
        return sorted(list(set(card_sets)))

    def shuffle(self) -> None:
        '''
        Shuffles this list of cards in-place.
        '''
        random.shuffle(self.data)

    def statistics(self, precision: int = 2) -> dict[str, int | float]:
        '''
        Computes helpful statistics associated with this collection of cards.

        Note:
          See the source of this method to get an idea of what the output `dict`
          looks like.

        Tip: Warning
          Cards with variable or no value for certain fields will be excluded
          from that field's calculations.

        Args:
          precision: Specifies the number of decimal places any `float` result will be rounded to.

        Returns:
          A `dict` containing the results of various statistical functions.
        '''
        return {
            'count': len(self.data),
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
            'num_blue': self.num_blue(),
            'num_red': self.num_red(),
            'num_yellow': self.num_yellow(),
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
        Computes the standard deviation of card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of card cost in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_defense(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of card defense in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_health(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of health in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.health for x in self.data if isinstance(x.health, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_intelligence(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of intelligence in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_pitch(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of pitch value in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def stdev_power(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of attack power in the list.
        '''
        if len(self.data) < 2: return 0.0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if len(array) >= 2:
            return round(stdev(array), precision)
        else:
            return 0.0

    def to_dataframe(self) -> DataFrame:
        '''
        Converts the list of cards into a [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

        Returns:
          A pandas `DataFrame` object representing the list of cards.
        '''
        return DataFrame(self.data)

    def to_json(self) -> str:
        '''
        Converts the list of cards to a JSON string representation.

        Returns:
          A JSON string representation of the list of cards.
        '''
        return json.dumps(self.to_list(), indent=JSON_INDENT)

    def to_list(self) -> list[dict[str, Any]]:
        '''
        Converts the list of cards into a raw Python list with nested
        dictionaries.

        Returns:
          A `list` of `dict` objects containing only Python primitives.
        '''
        return [card.to_dict() for card in self.data]

    def tokens(self) -> CardList:
        '''
        Returns the set of all token cards in this card list.

        Returns:
          The set of token cards in the list.
        '''
        return CardList([card for card in self.data if card.is_token()])

    def total_cost(self) -> int:
        '''
        Computes the total card cost within this card list.

        Tip: Warning
          Cards with variable or no cost are ignored.

        Returns:
          The total cost of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.cost for x in self.data if isinstance(x.cost, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_defense(self) -> int:
        '''
        Computes the total card defense within this card list.

        Tip: Warning
          Cards with variable or no defense are ignored.

        Returns:
          The total defense of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.defense for x in self.data if isinstance(x.defense, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_health(self) -> int:
        '''
        Computes the total card health within this card list.

        Tip: Warning
          Cards with variable or no health are ignored.

        Returns:
          The total health of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.health for x in self.data if isinstance(x.health, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_intelligence(self) -> int:
        '''
        Computes the total card intelligence within this card list.

        Tip: Warning
          Cards with variable or no intelligence are ignored.

        Returns:
          The total intelligence of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.intelligence for x in self.data if isinstance(x.intelligence, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_pitch(self) -> int:
        '''
        Computes the total card pitch within this card list.

        Tip: Warning
          Cards with variable or no pitch are ignored.

        Returns:
          The total pitch value of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.pitch for x in self.data if isinstance(x.pitch, int)]
        if array:
            return sum(array)
        else:
            return 0

    def total_power(self) -> int:
        '''
        Computes the total card power within this card list.

        Tip: Warning
          Cards with variable or no power are ignored.

        Returns:
          The total attack power of all cards in the list.
        '''
        if len(self.data) < 1: return 0
        array = [x.power for x in self.data if isinstance(x.power, int)]
        if array:
            return sum(array)
        else:
            return 0

    def types(self) -> list[str]:
        '''
        Returns the set of all card types in this card list.

        Returns:
          The unique `list` of all card types in the list.
        '''
        res = []
        for card in self.data:
            res.extend(card.types)
        return sorted(list(set(res)))

    def type_texts(self) -> list[str]:
        '''
        Returns the set of all type texts in this card list.

        Returns:
          The unique `list` of all card types in the list.
        '''
        return sorted(list(set([card.type_text for card in self.data])))

    def weapons(self) -> CardList:
        '''
        Returns the set of all weapon cards in this card list.

        Returns:
          The set of all weapon cards in the list.
        '''
        return CardList([card for card in self.data if card.is_weapon()])
