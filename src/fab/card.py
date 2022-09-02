'''
Contains the definitions of Flesh and Blood cards and card lists.
'''

from __future__ import annotations

import copy
import dataclasses
import datetime
import json

from IPython.display import display, Image
from typing import Any, cast, Optional

from .card_base import CardBase
from .card_base import STRING_FIELDS as BASE_STRING_FIELDS
from .card_base import STRING_LIST_FIELDS as BASE_STRING_LIST_FIELDS
from .card_base import VALUE_FIELDS as BASE_VALUE_FIELDS
from .meta import RARITIES

DATE_FORMAT = '%Y/%m/%d'

STRING_FIELDS = BASE_STRING_FIELDS

STRING_LIST_FIELDS = BASE_STRING_LIST_FIELDS | {
    # field: (plural desc, singular desc)
    'art_types': ('Art Types', 'Art Type'),
    'editions': ('Editions', 'Edition'),
    'foilings': ('Foiling Codes', 'Foiling Code'),
    'identifiers': ('Identifiers', 'Identifier'),
    'rarities': ('Rarities', 'Rarity'),
    'sets': ('Sets', 'Set'),
    'variations': ('Card Variations', 'Card Variation')
}

VALUE_FIELDS = BASE_VALUE_FIELDS

@dataclasses.dataclass
class Card(CardBase):
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

    The `dates` dictionary maps variation strings to tuples of the form
    `(<release date>, <out-of-print date>)`, where either tuple value may also
    be `None` if unknown or not applicable.

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
    subtypes (`subtypes`) and supertypes (`supertypes`). If The card contains
    one or more class supertypes, the `class_types` field will contain those
    types. Likewise if a card contains one or more talent supertypes, the
    `talent_types` field contain those types. Again, see the constants defined
    in the `meta` submodule to learn the possible values.

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
        class_types      = ['Runeblade'],
        color            = None,
        cost             = None,
        dates            = {'CHN001-N-R-R-S': ('...', '...')},
        defense          = None,
        editions         = ['F', 'N', 'U'],
        effect_keywords  = ['Create'],
        flavor_text      = None,
        foilings         = ['S', 'R', 'C'],
        full_name        = 'Chane',
        grants_keywords  = ['Go again'],
        identifiers      = ['HER037', 'CHN001', 'MON154'],
        image_urls       = {'CHN001-N-R-R-S': 'https://...', 'HER037-N-P-C-S': 'https://...'},
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
        talent_types     = ['Shadow'],
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

    Note that the fields/attributes associated with `Card` objects also include
    those defined in `CardBase` objects.

    Attributes:
      art_types: The list of art type codes associated with the card, sorted by rarity.
      dates: A dictionary correlating the initial release and out-of-print dates for a particular variation.
      editions: The list of edition codes the card was printed in.
      foilings: The list of foiling codes the card was printed in, sorted by foil rarity.
      identifiers: The list of card identifiers, such as `RNR012`.
      image_urls: A map of card variations to the URL of their appropriate image.
      rarities: The list of rarity codes associated with the card, sorted by rarity.
      sets: The list of card set codes associated with the card.
      variations: The list of unique variation IDs associated with the card (see above).
    '''
    art_types: list[str]
    dates: dict[str, tuple[Optional[datetime.date], Optional[datetime.date]]]
    editions: list[str]
    foilings: list[str]
    identifiers: list[str]
    image_urls: dict[str, str]
    rarities: list[str]
    sets: list[str]
    variations: list[str]

    def check_consistency(self) -> tuple[bool, Optional[str]]:
        '''
        Checks the consistency of this card, returning information on whether
        there are any invalid card fields.

        Returns:
          A tuple of the form `(<is consistent?>, <optional reason>)`.
        '''
        for variation in self.variations:
            chunks = variation.split('-')
            if len(chunks) != 5:
                return (False, f'Card variation "{variation}" not of the form "IDENTIFIER-EDITION-RARITY-FOILING-ARTTYPE"')
            if not chunks[0] in self.identifiers:
                return (False, f'Identifier for variation "{variation}" not present in self.identifiers')
            if not chunks[1] in self.editions:
                return (False, f'Edition for variation "{variation}" not present in self.editions')
            if not chunks[2] in self.rarities:
                return (False, f'Rarity for variation "{variation}" not present in self.rarities')
            if not chunks[3] in self.foilings:
                return (False, f'Foiling for variation "{variation}" not present in self.foilings')
            if not chunks[4] in self.art_types:
                return (False, f'Art type for variation "{variation}" not present in self.art_types')
            if not any(chunks[0].startswith(s) for s in self.sets):
                return (False, f'Card set for variation "{variation}" not present in self.sets')
        for variation in self.image_urls.keys():
            if not variation in self.variations:
                return (False, f'Card image URLs contains variation "{variation}" not present in self.variations')
        for variation in self.dates.keys():
            if not variation in self.variations:
                return (False, f'Card dates map contains variation "{variation}" not present in self.variations')
        return super().check_consistency()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Card:
        '''
        Creates a card from its dictionary representation.

        This method will automatically convert date strings to `datetime.date`
        objects if needed.

        Args:
          data: The dictionary representation of the card to convert from.

        Returns:
          A new card from the specified data.
        '''
        intermediate = {}
        for field, field_value in data.items():
            if field == 'dates':
                intermediate['dates'] = {}
                for k, v in field_value.items():
                    if v[0] is None:
                        ird = None
                    elif isinstance(v[0], str):
                        ird = datetime.datetime.strptime(v[0], DATE_FORMAT).date()
                    elif isinstance(v[0], datetime.date):
                        ird = v[0]
                    else:
                        raise ValueError('unknown initial release date format')
                    if v[1] is None:
                        oop = None
                    elif isinstance(v[1], str):
                        oop = datetime.datetime.strptime(v[1], DATE_FORMAT).date()
                    elif isinstance(v[1], datetime.date):
                        oop = v[1]
                    else:
                        raise ValueError('unknown out-of-print date format')
                    intermediate['dates'][k] = (ird, oop)
            else:
                intermediate[field] = field_value
        return Card(**intermediate)

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
        from .card_catalog import DEFAULT_CATALOG
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
        from .card_catalog import DEFAULT_CATALOG
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
          A new `Card` object from the parsed data.
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

    def image(self, height: int = 314, variation: Optional[str] = None, width: int = 225) -> Any:
        '''
        Display an image of this card, optionally providing an alternative
        variation to use.

        Args:
          height: The height to scale the resulting image to, in pixels.
          variation: The target `image_urls` variation to fetch image data for, or `None` to select the first image.
          width: The width to scale the resulting image to, in pixels.

        Returns:
          The image representation of the card.
        '''
        if not self.image_urls: return 'No images available'
        if variation is None:
            index = list(self.image_urls.keys())[0]
        else:
            index = variation
        return display(Image(self.image_urls[index], height=height, width=width))

    def initial_release_date(self) -> Optional[datetime.date]:
        '''
        Computes the initial release date associated with this card.

        Returns:
          The earliest release date associated with the card, or `None`.
        '''
        earliest = None
        for date in self.release_dates().values():
            if date is None: continue
            if earliest is None or date < earliest:
                earliest = copy.deepcopy(date)
        return earliest

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

    def out_of_print_dates(self) -> dict[str, Optional[datetime.date]]:
        '''
        Returns a mapping of card variations to their out-of-print dates.

        Returns:
          A mapping of card variations to their out-of-print dates.
        '''
        return {k: v[1] for k, v in self.dates.items()}

    def rarity_names(self) -> list[str]:
        '''
        Returns the full names of the rarities associated with this card.

        Returns:
          A `list` of card rarity names associated with the card.
        '''
        return [RARITIES[r] for r in self.rarities]

    def release_dates(self) -> dict[str, Optional[datetime.date]]:
        '''
        Returns a mapping of card variations to their release dates.

        Returns:
          A mapping of card variations to their release dates.
        '''
        return {k: v[0] for k, v in self.dates.items()}

    def to_dict(self, convert_dates: bool = True) -> dict[str, Any]:
        '''
        Converts this card into a raw python dictionary.

        Args:
          convert_dates: Whether to convert internal `datetime.date` objects into strings.

        Returns:
          A copy of the raw `dict` representation of the card.
        '''
        intermediate = {}
        for field, field_value in copy.deepcopy(self.__dict__).items():
            if field == 'dates':
                intermediate['dates'] = {}
                for k, v in cast(dict[str, tuple[Optional[datetime.date], Optional[datetime.date]]], field_value).items():
                    if convert_dates:
                        ird = None if v[0] is None else v[0].strftime(DATE_FORMAT)
                        oop = None if v[1] is None else v[1].strftime(DATE_FORMAT)
                        intermediate['dates'][k] = [ird, oop]
                    else:
                        intermediate['dates'][k] = [v[0], v[1]]
            else:
                intermediate[field] = field_value
        return intermediate
