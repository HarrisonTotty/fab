'''
Contains the definition of `CardVariant`.
'''

from __future__ import annotations

import copy
import dataclasses
import datetime
import json

from IPython.display import display, Image
from typing import Any, cast, Optional

from .parse import decompose_variation_str
from .card import Card
from .card_base import CardBase

DATE_FORMAT = '%Y/%m/%d'

@dataclasses.dataclass
class CardVariant(CardBase):
    '''
    Represents a particular variant of Flesh and Blood card.

    This object is similar to regular `Card` objects except that it is a
    completely unique variant, rather than a generalization over all cards
    of the same (full) name.

    Note that the fields/attributes associated with `CardVariant` objects also
    include those defined in `CardBase` objects.

    Attributes:
      art_type: The art type code associated with the card.
      card_set: The card set code associated with the card.
      edition: The edition code associated with the card.
      foiling: The foiling code associated with the card.
      identifier: The identifier of the card, such as `RNR012`.
      image_url: A URL associated with the card's image.
      out_of_print_date: The out-of-print date of the card, if applicable.
      rarity: The rarity code of the card.
      release_date: The release date of the card, if applicable.
      uid: The unique variation ID associated with the card.
    '''
    art_type: str
    card_set: str
    edition: str
    foiling: str
    identifier: str
    image_url: Optional[str]
    out_of_print_date: Optional[datetime.date]
    rarity: str
    release_date: Optional[datetime.date]
    uid: str

    def check_consistency(self) -> tuple[bool, Optional[str]]:
        '''
        Checks the consistency of this card, returning information on whether
        there are any invalid card fields.

        Returns:
          A tuple of the form `(<is consistent?>, <optional reason>)`.
        '''
        chunks = self.uid.split('-')
        if len(chunks) != 5:
            return (False, f'Card uid "{self.uid}" not of the form "IDENTIFIER-EDITION-RARITY-FOILING-ARTTYPE"')
        if self.art_type != chunks[4]:
            return (False, f'Card art type "{self.art_type}" not consistent with uid "{self.uid}"')
        if not chunks[0].startswith(self.card_set):
            return (False, f'Card set "{self.card_set}" not consistent with uid "{self.uid}"')
        if self.edition != chunks[1]:
            return (False, f'Card edition "{self.edition}" not consistent with uid "{self.uid}"')
        if self.foiling != chunks[3]:
            return (False, f'Card foiling "{self.foiling}" not consistent with uid "{self.uid}"')
        if self.identifier != chunks[0]:
            return (False, f'Card identifier "{self.identifier}" not consistent with uid "{self.uid}"')
        if self.rarity != chunks[2]:
            return (False, f'Card rarity "{self.rarity}" not consistent with uid "{self.uid}"')
        return super().check_consistency()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> CardVariant:
        '''
        Creates a card variant from its dictionary representation.

        This method will automatically convert date strings to `datetime.date`
        objects if needed.

        Args:
          data: The dictionary representation of the card variant to convert from.

        Returns:
          A new card variant from the specified data.
        '''
        intermediate = {}
        for field, field_value in data.items():
            if field in ['out_of_print_date', 'release_date']:
                if field_value is None:
                    val = None
                elif isinstance(field_value, str):
                    val = datetime.datetime.strptime(field_value, DATE_FORMAT).date()
                elif isinstance(field_value, datetime.date):
                    val = field_value
                intermediate[field] = val
            else:
                intermediate[field] = field_value
        return CardVariant(**intermediate)

    @staticmethod
    def from_json(jsonstr: str) -> CardVariant:
        '''
        Creates a new card variant from the specified JSON string.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `CardVariant` object from the parsed data.
        '''
        return CardVariant.from_dict(json.loads(jsonstr))

    @staticmethod
    def from_variation(variation: str) -> CardVariant:
        '''
        Constructs a card variant from its variation code.

        Note:
          To instantiate the card this way, the default card catalog must be
          instantiated.

        Args:
          variation: The variation code of the card.

        Returns:
          A new card variant from the parsed data.
        '''
        from .card_catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('specified card catalog has not been initialized')
        base = DEFAULT_CATALOG.lookup_card(variation=variation).to_base_dict()
        vdata = decompose_variation_str(variation)
        for k, v in vdata.items():
            if k == 'set':
                base['card_set'] = v
            else:
                base[k] = v
        base['uid'] = variation
        return CardVariant.from_dict(base)

    def image(self, height: int = 314, width: int = 225) -> Any:
        '''
        Display the image of this card.

        Args:
          height: The height to scale the resulting image to, in pixels.
          width: The width to scale the resulting image to, in pixels.

        Returns:
          The image representation of the card.
        '''
        if self.image_url is None: return 'No images available'
        return display(Image(self.image_url, height=height, width=width))

    def to_dict(self, convert_dates: bool = True) -> dict[str, Any]:
        '''
        Converts this card into a raw python dictionary.

        Args:
          convert_dates: Whether to convert internal `datetime.date` objects into strings.

        Returns:
          A copy of the raw `dict` representation of the card.
        '''
        if not convert_dates:
            return super().to_dict()
        intermediate = {}
        for field, field_value in copy.deepcopy(self.__dict__).items():
            if field in ['out_of_print_date', 'release_date']:
                fv = cast(Optional[datetime.date], field_value)
                intermediate[field] = None if fv is None else fv.strftime(DATE_FORMAT)
            else:
                intermediate[field] = field_value
        return intermediate

    def to_card(self) -> Card:
        '''
        Converts this card variant into its generalized `Card` counterpart.

        Note:
          To instantiate the card this way, the default card catalog must be
          instantiated.

        Returns:
          The generalized `Card` object associated with this variant.
        '''
        from .card_catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('specified card catalog has not been initialized')
        return DEFAULT_CATALOG.lookup_card(variation=self.uid)
