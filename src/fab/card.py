'''
Contains the definitions of Flesh and Blood cards and card lists.
'''

from __future__ import annotations

import copy
import dataclasses
import json

from IPython.display import display, Image, Markdown
from pandas import Series
from typing import Any, Optional, Union

from .meta import GAME_FORMATS, ICON_CODE_IMAGE_URLS, RARITIES

STRING_FIELDS = {
    # field: desc
    'body': 'Body Text',
    'card_type': 'Primary Type',
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
    'art_types': ('Art Types', 'Art Type'),
    'editions': ('Editions', 'Edition'),
    'effect_keywords': ('Effect Keywords', 'Effect Keyword'),
    'foilings': ('Foiling Codes', 'Foiling Code'),
    'grants_keywords': ('Grants Keywords', 'Grants Keyword'),
    'identifiers': ('Identifiers', 'Identifier'),
    'image_urls': ('Image URLs', 'Image URL'),
    'keywords': ('Keywords', 'Keyword'),
    'label_keywords': ('Label Keywords', 'Label Keyword'),
    'rarities': ('Rarities', 'Rarity'),
    'sets': ('Sets', 'Set'),
    'subtypes': ('Subtypes', 'Subtype'),
    'supertypes': ('Supertypes', 'Supertype'),
    'tags': ('User Tags', 'User Tag'),
    'token_keywords': ('Token Keywords', 'Token Keyword'),
    'types': ('Types', 'Type'),
    'type_keywords': ('Type Keywords', 'Type Keyword'),
    'variations': ('Card Variations', 'Card Variation')
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

JSON_INDENT: Optional[int] = 2

TCGPLAYER_BASE_URL = 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q='

@dataclasses.dataclass
class Card:
    '''
    Represents a Flesh and Blood card.

    `fab` treats all prints and versions of a card as under the same `Card`
    object. If any change is made to the card's body text or attributes between
    prints, it can be assumed that `fab` lists the latest print of the card. The
    "full name" (`full_name`) of a card is considered to be an extension of its
    "base name" (`name`) with the following formatting:

    ```
    {name} ({pitch})
    ```

    if the card has an integer pitch value. Otherwise, the full name of the card
    is the same as its base name.

    For numeric attributes such as `cost`, a value of `None` indicates that the
    attribute simply doesn't exist on the card (such as `health` on most
    non-hero cards). A `str` value typically indicates a variable value based on
    some condition described in the card's `body` text.

    The value of the `variations` attribute is a list of unique strings of the
    form:

    ```
    {identifier}-{edition}-{rarity}-{foiling}-{art_type}
    ```

    which defines the set of possible printing conditions associated with the
    card.

    The `keywords` field contains the set of all keywords associated with the
    card. The subset of those granted to _other_ cards are contained in the
    `grants_keywords` field. The `keywords` field is then further broken down
    into `ability_keywords`, `effect_keywords`, `label_keywords`,
    `token_keywords`, and `type_keywords`. It should be noted here that
    `type_keywords` is distinguished from `types`, in that it contains type
    keywords that exist within the `body` of the card, as opposed to the card's
    `type_text`. See the constants defined in the `meta` submodule for more
    information.

    Regarding card types, each card has a list of all type keywords (`types`), a
    primary type (`card_type`), and the subset of types which are considered
    subtypes (`subtypes`) and supertypes (`supertypes`). If The card contains a
    class supertype, the `class_type` field will be set to that type. Likewise
    if a card contains a talent supertype, the `talent_type` field will be set
    to that type. Again, see the constants defined in the `meta` submodule to
    learn the possible values.

    For user convenience, `Card` objects expose two additional metadata fields
    (`notes` and `tags`) which may be populated by the user for arbitrary use.

    Example:
      Manually instantiating a card object:

      ```python
      chane = Card(
        ability_keywords = ['Go again'],
        art_types        = ['S'],
        body             = '**Once per Turn Action** - Create a Soul Shackle token: Your ...',
        card_type        = 'Hero',
        class_type       = 'Runeblade',
        cost             = None,
        defense          = None,
        editions         = ['F', 'N', 'U'],
        effect_keywords  = ['Create'],
        flavor_text      = None,
        foilings         = ['S', 'R', 'C'],
        full_name        = 'Chane',
        grants_keywords  = ['Go again'],
        identifiers      = ['HER037', 'CHN001', 'MON154'],
        image_urls       = ['https://...', 'https://...'],
        intellect        = 4,
        keywords         = ['Action', 'Create', 'Go again', 'Soul Shackle'],
        label_keywords   = [],
        legality         = {'B': True, 'C': True, 'CC': True},
        life             = 20,
        name             = 'Chane',
        pitch            = None,
        power            = None,
        rarities         = ['T', 'R', 'P'],
        sets             = ['HER', 'CHN', 'MON'],
        subtypes         = ['Young'],
        supertypes       = ['Runeblade', 'Shadow'],
        talent_type      = 'Shadow',
        token_keywords   = ['Soul Shackle'],
        types            = ['Hero', 'Runeblade', 'Shadow', 'Young'],
        type_keywords    = ['Action'],
        type_text        = 'Shadow Runeblade Hero - Young',
        variations       = ['CHN001-N-R-R-S', 'HER037-N-P-C-S', 'MON154-F-T-S-S', 'MON154-U-T-S-S'],
        notes            = 'Chane is pretty cool. I might want to build a CC deck with him soon.',
        tags             = ['chane-cards', 'runeblades-i-like']
      )
      ```

      Creating a card from its known full name:

      ```python
      chane = Card.from_full_name('Chane')
      ```

      Creating a card from its known identifier:

      ```python
      chane = Card.from_identifier('MON154')
      ```

    Attributes:
      ability_keywords: The list of ability keywords associated with this card, such as `Dominate`.
      art_types: The list of art type codes associated with the card, sorted by rarity.
      body: The full body text (rules text and reminder text) of the card, in Markdown format.
      card_type: The primary type associated with the card, such as `Action`.
      class_type: The hero class supertype associated with the card, or `None` if not applicable.
      cost: The resource cost of the card, or `None` if not present.
      defense: The defense value of the card, or `None` if not present.
      effect_keywords: The list of effect keywords associated with this card, such as `Discard`.
      editions: The list of edition codes the card was printed in.
      flavor_text: Any lore text printed on the body of the card, in Markdown format.
      foilings: The list of foiling codes the card was printed in, sorted by foil rarity.
      full_name: The full name of the card, including pitch value.
      grants_keywords: A list of keywords this card grants to other cards.
      identifiers: The list of card identifiers, such as `RNR012`.
      image_urls: A list of card image URLs.
      intellect: The intellect value of the card, or `None` if not present.
      keywords: The list of all keywords associated with the card.
      label_keywords: The list of label keywords associated with this card, such as `Combo`.
      legality: Whether this card is _currently_ legal for various formats.
      life: The life (health) value of the card, or `None` if not present.
      name: The name of the card, excluding pitch value.
      notes: An optional string of user notes associated with the card, in Markdown format.
      pitch: The pitch value of the card, or `None` if not present.
      power: The attack power of the card, or `None` if not present.
      rarities: The list of rarity codes associated with the card, sorted by rarity.
      sets: The list of card set codes associated with the card.
      subtypes: The list of subtypes associated with this card.
      supertypes: The list of supertypes associated with this card.
      tags: A collection of user-defined tags.
      talent_type: The talent supertype associated with this card (see `meta.TALENT_SUPERTYPES`), or `None` if not applicable.
      token_keywords: The list of all token keywords associated with this card, such as `Frostbite`.
      types: The list of all type keywords contained within the `type_text` of this card.
      type_keywords: The list of type keywords present within the `body` of the card, such as `Action`.
      type_text: The full type box text of the card.
      variations: The list of unique variation IDs associated with the card (see above).
    '''

    ability_keywords: list[str]
    art_types: list[str]
    body: Optional[str]
    card_type: str
    class_type: Optional[str]
    cost: Optional[int | str]
    defense: Optional[int | str]
    editions: list[str]
    effect_keywords: list[str]
    flavor_text: Optional[str]
    foilings: list[str]
    full_name: str
    grants_keywords: list[str]
    identifiers: list[str]
    image_urls: list[str]
    intellect: Optional[int | str]
    keywords: list[str]
    label_keywords: list[str]
    legality: dict[str, bool]
    life: Optional[int | str]
    name: str
    pitch: Optional[int | str]
    power: Optional[int | str]
    rarities: list[str]
    sets: list[str]
    subtypes: list[str]
    supertypes: list[str]
    talent_type: Optional[str]
    token_keywords: list[str]
    types: list[str]
    type_keywords: list[str]
    type_text: str
    variations: list[str]
    notes: Optional[str] = None
    tags: list[str] = dataclasses.field(default_factory=list)

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

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Card:
        '''
        Creates a card from its dictionary representation.

        Args:
          data: The dictionary representation of the card to convert from.

        Returns:
          A new card from the specified data.
        '''
        return Card(**data)

    @staticmethod
    def from_full_name(full_name: str) -> Card:
        '''
        Creates a new card from its full name.

        Note:
          To instantiate the card this way, the default card catalog must be
          instantiated.

        Args:
          full_name: The full name of the card (including pitch value, if applicable).

        Returns:
          A new `Card` object.
        '''
        from .catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('default card catalog has not been initialized')
        return DEFAULT_CATALOG.lookup_card(full_name=full_name)

    @staticmethod
    def from_identifier(identifier: str) -> Card:
        '''
        Creates a new card from its identifier.

        Note:
          To instantiate the card this way, the default card catalog must be
          instantiated.

        Args:
          identifier: The identifier of the card.

        Returns:
          A new `Card` object.
        '''
        from .catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('specified card catalog has not been initialized')
        return DEFAULT_CATALOG.lookup_card(identifier=identifier)

    @staticmethod
    def from_json(jsonstr: str) -> Card:
        '''
        Creates a new card from the specified JSON string.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `Card` object.
        '''
        return Card.from_dict(json.loads(jsonstr))

    def highest_rarity(self) -> str:
        '''
        Returns the highest possible rarity associated with the card.

        Returns:
          The rarity code of the highest possible rarity associated with the card.
        '''
        if not self.rarities:
            raise Exception('card does not contain any rarities')
        highest = -1
        for rarity in self.rarities:
            level = list(RARITIES.keys()).index(rarity)
            if level > highest:
                highest = level
        return list(RARITIES.keys())[highest]

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

    def lowest_rarity(self) -> str:
        '''
        Returns the lowest possible rarity associated with the card.

        Returns:
          The rarity code of the lowest possible rarity associated with the card.
        '''
        if not self.rarities:
            raise Exception('card does not contain any rarities')
        lowest = 100
        for rarity in self.rarities:
            level = list(RARITIES.keys()).index(rarity)
            if level < lowest:
                lowest = level
        return list(RARITIES.keys())[lowest]

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


