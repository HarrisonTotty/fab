'''
Contains definitions associated with tracking personal card inventories.
'''

from __future__ import annotations

import copy
import json
import os

from collections import UserDict
from typing import Optional

from . import parse
from .card_list import CardList
from .meta import ART_TYPES, EDITIONS, FOILINGS, RARITIES

JSON_INDENT: Optional[int] = 2

class CardInventory(UserDict[str, int]):
    '''
    Represents an inventory of unique Flesh and Blood cards.

    This is essentially a `dict[str, int]`, mapping card variation IDs to their
    counts.

    Note:
      This class inherits `collections.UserDict`, and thus supports any common
      `dict` methods.

    Tip: Warning
      Note that since this object is essentially a `dict`, calling `len()` on it
      will _not_ return the total number of cards in the inventory. Instead, it
      returns the total number of _different types_ of cards in the inventory.
      To get the overall number of cards in the inventory, use the `count()`
      method.

    Attributes:
      data: The underlying mapping of card variation codes to inventory counts.
    '''
    data: dict[str, int]

    def add(
        self,
        identifier: str,
        rarity: str,
        foiling: str,
        art_type: str = 'S',
        count: int = 1,
        edition: str = 'U',
    ) -> None:
        '''
        Adds one or more copies of a unique card to this inventory.

        Args:
          art_type: The art type code of the card.
          count: The number of copies to add to the inventory.
          edition: The edition code of the card.
          foiling: The foiling code of the card.
          identifier: The identifier of the card to add.
          rarity: The rarity code of the card.
        '''
        if not art_type in ART_TYPES:
            raise ValueError(f'specified card art type code not one of {list(ART_TYPES.keys())}')
        if not edition in EDITIONS:
            raise ValueError(f'specified card edition code not one of {list(EDITIONS.keys())}')
        if not foiling in FOILINGS:
            raise ValueError(f'specified card foiling code not one of {list(FOILINGS.keys())}')
        if not rarity in RARITIES:
            raise ValueError(f'specified card rarity code not one of {list(RARITIES.keys())}')
        variation = parse.compose_variation_str(
            art_type = art_type,
            edition = edition,
            foiling = foiling,
            identifier = identifier,
            rarity = rarity
        )
        if variation in self.data:
            self.data[variation] += count
        else:
            self.data[variation] = count

    def count(self) -> int:
        '''
        Computes the total number of cards in this inventory.

        Return:
          The total number of cards in the inventory.
        '''
        return sum(self.data.values())

    @staticmethod
    def from_dict(data: dict[str, int]) -> CardInventory:
        '''
        Parses a new card inventory from the specified `dict` representation.

        Args:
          data: The `dict` representation to parse.

        Returns:
          A new `CardInventory` from the parsed data.
        '''
        return CardInventory(data)

    @staticmethod
    def from_json(jsonstr: str) -> CardInventory:
        '''
        Parses a new card inventory from the specified JSON string representation.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `CardInventory` from the parsed data.
        '''
        return CardInventory.from_dict(json.loads(jsonstr))

    @staticmethod
    def load(file_path: str) -> CardInventory:
        '''
        Loads a card inventory from the specified `.json` file.

        Args:
          file_path: The `.json` file path from which to load the inventory.

        Returns:
          The parsed card inventory object loaded from the specified file path.
        '''
        with open(os.path.expanduser(file_path), 'r') as f:
            if file_path.endswith('.json'):
                return CardInventory.from_json(f.read())
            else:
                raise Exception('specified file path is not a JSON file')

    def save(self, file_path: str) -> None:
        '''
        Saves the card inventory to the specified `.json` file path.

        Args:
          file_path: The `.json` file path to save to.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            else:
                raise Exception('specified file path is not a JSON file')

    def set(
        self,
        identifier: str,
        rarity: str,
        foiling: str,
        art_type: str = 'S',
        count: int = 1,
        edition: str = 'U',
    ) -> None:
        '''
        Sets the number of copies associated with a unique card.

        Note:
          Setting a card's count to `0` does not delete the item from the
          inventory but rather simply sets the count to `0`. This is useful for
          tracking when you _used_ to own a card, or when _plan_ to obtain a
          copy of a particular card.

        Args:
          art_type: The art type code of the card.
          count: The number of copies to set the inventory count to.
          edition: The edition code of the card.
          foiling: The foiling code of the card.
          identifier: The identifier of the card.
          rarity: The rarity code of the card.
        '''
        if not art_type in ART_TYPES:
            raise ValueError(f'specified card art type code not one of {list(ART_TYPES.keys())}')
        if not edition in EDITIONS:
            raise ValueError(f'specified card edition code not one of {list(EDITIONS.keys())}')
        if not foiling in FOILINGS:
            raise ValueError(f'specified card foiling code not one of {list(FOILINGS.keys())}')
        if not rarity in RARITIES:
            raise ValueError(f'specified card rarity code not one of {list(RARITIES.keys())}')
        variation = parse.compose_variation_str(
            art_type = art_type,
            edition = edition,
            foiling = foiling,
            identifier = identifier,
            rarity = rarity
        )
        self.data[variation] = count

    def to_cardlist(self) -> CardList:
        '''
        Converts this unique card inventory into a list of generic
        representations of cards.

        Note:
          To instantiate the card list this way, the default card catalog must
          be initialized.

        Returns:
          A `CardList` object containing the generic representations of the cards contained within this inventory.
        '''
        from .card_catalog import DEFAULT_CATALOG
        if DEFAULT_CATALOG is None:
            raise Exception('specified card catalog has not been initialized')
        cards = []
        for k, v in self.data.items():
            for _ in range(0, v):
                cards.append(DEFAULT_CATALOG.lookup_card(variation=k))
        return CardList(cards)

    def to_dict(self) -> dict[str, int]:
        '''
        Converts the inventory object into a raw dictionary of python
        primitives.

        Returns:
          A raw `dict` representation of the card inventory.
        '''
        return copy.deepcopy(self.data)

    def to_json(self) -> str:
        '''
        Computes the JSON string representation of the inventory.

        Returns:
          The JSON string representation of the card inventory.
        '''
        return json.dumps(self.to_dict(), indent=JSON_INDENT)
