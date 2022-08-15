'''
Contains the definition of `CardBase`.
'''

from __future__ import annotations

import copy
import dataclasses
import json

from IPython.display import display, Markdown
from pandas import Series
from typing import Any, Optional, Union

from .meta import ICON_CODE_IMAGE_URLS

JSON_INDENT: Optional[int] = None
TCGPLAYER_BASE_URL = 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q='

STRING_FIELDS = {
    # field: desc
    'body': 'Body Text',
    'card_type': 'Primary Type',
    'color': 'Color',
    'class_type': 'Class',
    'flavor_text': 'Flavor Text',
    'full_name': 'Full Name',
    'name': 'Name',
    'notes': 'User Notes',
    'talent_type': 'Talent',
    'type_text': 'Type Box Text'
}

STRING_LIST_FIELDS = {
    # field: (plural desc, singular desc)
    'ability_keywords': ('Ability Keywords', 'Ability Keyword'),
    'effect_keywords': ('Effect Keywords', 'Effect Keyword'),
    'grants_keywords': ('Grants Keywords', 'Grants Keyword'),
    'keywords': ('Keywords', 'Keyword'),
    'label_keywords': ('Label Keywords', 'Label Keyword'),
    'subtypes': ('Subtypes', 'Subtype'),
    'supertypes': ('Supertypes', 'Supertype'),
    'tags': ('User Tags', 'User Tag'),
    'token_keywords': ('Token Keywords', 'Token Keyword'),
    'types': ('Types', 'Type'),
    'type_keywords': ('Type Keywords', 'Type Keyword'),
}

VALUE_FIELDS = {
    # field: desc
    'cost': 'Resource Cost',
    'defense': 'Defense Value',
    'intellect': 'Intellect',
    'life': 'Life Value',
    'pitch': 'Pitch Value',
    'power': 'Attack Power'
}

@dataclasses.dataclass
class CardBase:
    '''
    Represents the base properties of cards which are present whether concerning
    generic `Card` objects or unique `CardVariant` objects.

    This class isn't usually instantiated directly. Instead, you'll most likely
    want to work with `Card` or `CardVariant` objects.

    Attributes:
      ability_keywords: The list of ability keywords associated with this card, such as `Dominate`.
      body: The full body text (rules text and reminder text) of the card, in Markdown format.
      card_type: The primary type associated with the card, such as `Action`.
      class_type: The hero class supertype associated with the card, or `None` if not applicable.
      color: The color of the card, being `"Red"`, `"Yellow"`, `"Blue"`, or `None`.
      cost: The resource cost of the card, or `None` if not present.
      defense: The defense value of the card, or `None` if not present.
      effect_keywords: The list of effect keywords associated with this card, such as `Discard`.
      flavor_text: Any lore text printed on the body of the card, in Markdown format.
      full_name: The full name of the card, including pitch value.
      grants_keywords: A list of keywords this card grants to other cards.
      intellect: The intellect value of the card, or `None` if not present.
      keywords: The list of all keywords associated with the card.
      label_keywords: The list of label keywords associated with this card, such as `Combo`.
      legality: Whether this card is _currently_ legal for various formats.
      life: The life (health) value of the card, or `None` if not present.
      name: The name of the card, excluding pitch value.
      notes: An optional string of user notes associated with the card, in Markdown format.
      pitch: The pitch value of the card, or `None` if not present.
      power: The attack power of the card, or `None` if not present.
      subtypes: The list of subtypes associated with this card.
      supertypes: The list of supertypes associated with this card.
      tags: A collection of user-defined tags.
      talent_type: The talent supertype associated with this card (see `meta.TALENT_SUPERTYPES`), or `None` if not applicable.
      token_keywords: The list of all token keywords associated with this card, such as `Frostbite`.
      types: The list of all type keywords contained within the `type_text` of this card.
      type_keywords: The list of type keywords present within the `body` of the card, such as `Action`.
      type_text: The full type box text of the card.
    '''
    ability_keywords: list[str]
    body: Optional[str]
    card_type: str
    class_type: Optional[str]
    color: Optional[str]
    cost: Optional[int | str]
    defense: Optional[int | str]
    effect_keywords: list[str]
    flavor_text: Optional[str]
    full_name: str
    grants_keywords: list[str]
    intellect: Optional[int | str]
    keywords: list[str]
    label_keywords: list[str]
    legality: dict[str, bool]
    life: Optional[int | str]
    name: str
    notes: Optional[str]
    pitch: Optional[int | str]
    power: Optional[int | str]
    subtypes: list[str]
    supertypes: list[str]
    tags: list[str]
    talent_type: Optional[str]
    token_keywords: list[str]
    type_keywords: list[str]
    type_text: str
    types: list[str]

    def __getitem__(self, key: str) -> Union[dict[str, bool], int, list[str], None, str]:
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
        return hash((self.name, self.pitch))

    def __str__(self) -> str:
        '''
        Computes the JSON string representation of the card.

        This is an alias of the `to_json()` method.

        Returns:
          The JSON string representation of the card.
        '''
        return self.to_json()

    def check_consistency(self) -> tuple[bool, Optional[str]]:
        '''
        Checks the consistency of this card, returning information on whether
        there are any invalid card fields.

        Returns:
          A tuple of the form `(<is consistent?>, <optional reason>)`.
        '''
        for k in self.ability_keywords:
            if not k in self.keywords:
                return (False, f'Ability keyword "{k}" not present in self.keywords')
        if not self.card_type in self.types:
            return (False, f'Primary card type "{self.card_type}" not present in self.types')
        if isinstance(self.class_type, str):
            if not self.class_type in self.supertypes:
                return (False, f'Card class type "{self.class_type}" not present in self.supertypes')
            if not self.class_type in self.types:
                return (False, f'Card class type "{self.class_type}" not present in self.types')
        if isinstance(self.color, str):
            if not self.color in ['Red', 'Yellow', 'Blue']:
                return (False, f'Card color "{self.color}" is not "Red", "Yellow", "Blue", or None')
            if self.color == 'Red' and (not isinstance(self.pitch, int) or self.pitch != 1):
                return (False, f'Card color "{self.color}" is inconsistent with card pitch value')
            if self.color == 'Yellow' and (not isinstance(self.pitch, int) or self.pitch != 2):
                return (False, f'Card color "{self.color}" is inconsistent with card pitch value')
            if self.color == 'Blue' and (not isinstance(self.pitch, int) or self.pitch != 3):
                return (False, f'Card color "{self.color}" is inconsistent with card pitch value')
        if isinstance(self.cost, int) and self.cost < 0:
            return (False, f'Card cost "{self.cost}" is a negative number')
        if isinstance(self.defense, int) and self.defense < 0:
            return (False, f'Card defense "{self.defense}" is a negative number')
        for k in self.effect_keywords:
            if not k in self.keywords:
                return (False, f'Effect keyword "{k}" not present in self.keywords')
        if isinstance(self.intellect, int) and self.intellect < 0:
            return (False, f'Card intellect "{self.intellect}" is a negative number')
        if isinstance(self.pitch, int):
            if self.full_name != f'{self.name} ({self.pitch})':
                return (False, f'Card full name "{self.full_name}" is not of the form "NAME (PITCH)"')
        for k in self.label_keywords:
            if not k in self.keywords:
                return (False, f'Label keyword "{k}" not present in self.keywords')
        if isinstance(self.life, int) and self.life < 0:
            return (False, f'Card life value "{self.life}" is a negative number')
        if not self.name:
            return (False, 'self.name is empty')
        if isinstance(self.pitch, int):
            if self.pitch < 0:
                return (False, f'Card pitch value "{self.pitch}" is a negative number')
            if not isinstance(self.color, str):
                return (False, f'Card specifies pitch value of "{self.pitch}" but no corresponding color')
        if isinstance(self.power, int) and self.power < 0:
            return (False, f'Card attack power "{self.power}" is a negative number')
        for t in self.subtypes:
            if not t in self.types:
                return (False, f'Card subtype "{t}" not present in self.types')
        for t in self.supertypes:
            if not t in self.types:
                return (False, f'Card supertype "{t}" not present in self.types')
        if isinstance(self.talent_type, str):
            if not self.talent_type in self.supertypes:
                return (False, f'Card talent type "{t}" not present in self.supertypes')
            if not self.talent_type in self.types:
                return (False, f'Card talent type "{t}" not present in self.types')
        for k in self.token_keywords:
            if not k in self.keywords:
                return (False, f'Token keyword "{k}" not present in self.keywords')
        for k in self.type_keywords:
            if not k in self.keywords:
                return (False, f'Type keyword "{k}" not present in self.keywords')
        if not self.types:
            return (False, 'self.types is empty')
        return (True, None)


    def cost_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the cost value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.cost if isinstance(self.cost, int) else None

    def defense_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the defense value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.defense if isinstance(self.defense, int) else None

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
        return False if self.color is None else self.color == 'Blue'

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

    def is_generic(self) -> bool:
        '''
        Whether this card is a generic card.

        Returns:
          Whether this card is a generic card.
        '''
        return 'Generic' in self.types

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
        return False if self.color is None else self.color == 'Red'

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
        return False if self.color is None else self.color == 'Yellow'

    def intellect_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the intellect value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.intellect if isinstance(self.intellect, int) else None

    def keys(self) -> list[str]:
        '''
        Returns the dictionary keys associated with this card class.

        Returns:
          The `dict` keys as `list[str]`, corresponding to the possible fields of the card.
        '''
        return list(self.__dict__.keys())

    def life_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the life value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.life if isinstance(self.life, int) else None

    def pitch_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the pitch value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.pitch if isinstance(self.pitch, int) else None

    def power_value(self) -> Optional[int]:
        '''
        Returns the integer representation of the power value of this card.

        If the actual value of the corresponding `Card` attribute is `None` or
        a `str`, this method will return `None`.

        Returns:
          The integer representation of the corresponding card field.
        '''
        return self.power if isinstance(self.power, int) else None

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
        if not self.intellect is None:
            mdstr += f'| Intellect | {self.intellect} |\n'
        if not self.life is None:
            mdstr += f'| Life | {self.life} |\n'
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

    def render_notes(self, icon_size: int = 11) -> Any:
        '''
        Renders the notes of this card as markdown output.

        Args:
          icon_size: Specified the target width of icon images.

        Returns:
          The IPython-rendered markdown output.
        '''
        if self.notes is None: return 'Specified card does not have any notes.'
        with_images = self.notes
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

    def to_base_dict(self) -> dict[str, Any]:
        '''
        Converts this card into a raw python dictionary.

        This method is different from `to_dict()` in that it only includes keys
        associated with `CardBase` objects.

        Returns:
          A copy of the raw `dict` representation of the card.
        '''
        result = {}
        for k in (list(STRING_FIELDS.keys()) + list(STRING_LIST_FIELDS.keys()) + list(VALUE_FIELDS.keys())):
            result[k] = self[k]
        return copy.deepcopy(result)

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
        return json.dumps(self.to_dict(), indent=JSON_INDENT)

    def to_series(self) -> Series:
        '''
        Converts the card into a [pandas Series
        object](https://pandas.pydata.org/docs/reference/series.html).

        Returns:
          A pandas `Series` object associated with the card.
        '''
        return Series(self.to_dict())
