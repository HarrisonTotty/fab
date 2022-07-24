'''
Contains definitions associated with tracking personal card inventories.
'''

from __future__ import annotations

import copy
import dataclasses
import json
import os

from collections import UserDict
from typing import Any, Optional

from .card import Card, CardList
from .meta import EDITIONS, FOILINGS, RARITIES

JSON_INDENT: Optional[int] = 2

@dataclasses.dataclass
class InventoryItem:
    '''
    Represents a particular instance of a Flesh and Blood card, for inventory
    purposes.

    Note:
      Unlike normal `Card` objects, `InventoryItem` objects represent a
      card's unique identifier, edition, rarity, and foiling.

    Attributes:
      edition: The edition code associated with the card (see `meta.EDITIONS`).
      foiling: The foiling code associated with the card (see `meta.FOILINGS`).
      identifier: The unique identifier associated with the card.
      rarity: The rarity code associated with the card (see `meta.RARITIES`).
    '''
    identifier: str
    rarity: str
    edition: str = 'U'
    foiling: str = 'S'

    def __getitem__(self, key: str) -> str:
        '''
        Allows one to access fields of an inventory item via dictionary syntax.

        Args:
          key: The name of the class attribute to fetch.

        Returns:
          The value associated with the specified field.
        '''
        return self.__dict__[key]

    def __hash__(self) -> Any:
        '''
        Computes the hash representation of the inventory item.

        Returns:
          The hash representation of the inventory item.
        '''
        return hash((self.edition, self.foiling, self.identifier, self.rarity))

    def __str__(self) -> str:
        '''
        Computes the string representation of the inventory item.

        This is an alias to the `to_str()` method.

        Returns:
          The string representation of the inventory item.
        '''
        return self.to_str()

    @staticmethod
    def from_json(jsonstr: str) -> InventoryItem:
        '''
        Creates a new inventory card from the specified JSON string.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          The parsed `InventoryItem` object.
        '''
        return InventoryItem.from_str(json.loads(jsonstr))

    @staticmethod
    def from_list(data: list[str]) -> InventoryItem:
        '''
        Creates a new inventory card from its list representation.

        Returns:
          The new inventory item.
        '''
        if not len(data) == 4:
            raise ValueError('input list does not contain exactly four elements')
        return InventoryItem(
            edition = data[0],
            foiling = data[1],
            identifier = data[2],
            rarity = data[3]
        )

    @staticmethod
    def from_tuple(data: tuple[str, str, str, str]) -> InventoryItem:
        '''
        Creates a new inventory card from its tuple representation.

        Returns:
          The new inventory item.
        '''
        if not len(data) == 4:
            raise ValueError('input list does not contain exactly four elements')
        return InventoryItem(
            edition = data[0],
            foiling = data[1],
            identifier = data[2],
            rarity = data[3]
        )

    @staticmethod
    def from_str(data: str) -> InventoryItem:
        '''
        Creates a new inventory card from its string representation.

        Returns:
          The new inventory item.
        '''
        parts = data.split('-')
        if not len(parts) == 4:
            raise ValueError('specified string not of the form "EDITION-IDENTIFIER-RARITY-FOILING"')
        return InventoryItem(
            edition = parts[0],
            foiling = parts[3],
            identifier = parts[1],
            rarity = parts[2]
        )

    def keys(self) -> list[str]:
        '''
        Returns the dictionary keys associated with this inventory item.

        Returns:
          The `dict` keys as `list[str]`, corresponding to the possible fields of the inventory item.
        '''
        return list(self.__dict__.keys())

    def to_card(self, catalog: Optional[CardList] = None) -> Card:
        '''
        Converts this unique card representation into a generic card
        representation.

        Note:
          To instantiate the card this way, a card catalog (`CardList`) must be
          provided, defaulting to `card.CARD_CATALOG`.

        Args:
          catalog: The card catalog to use as a reference, defaulting to `card.CARD_CATALOG` if `None`.

        Returns:
          A `Card` object associated with this inventory item.
        '''
        return Card.from_identifier(self.identifier, catalog=catalog)

    def to_dict(self) -> dict[str, str]:
        '''
        Converts this inventory item into a raw python dictionary.

        Returns:
          A copy of the raw `dict` representation of the inventory item.
        '''
        return copy.deepcopy(self.__dict__)

    def to_json(self) -> str:
        '''
        Computes the inventory item's JSON string representation.

        Returns:
          A JSON string representation of the inventory item.
        '''
        return json.dumps(self.to_str(), indent=JSON_INDENT)

    def to_list(self) -> list[str]:
        '''
        Converts this inventory item into a list of field strings.

        Returns:
          A `list` representation of the inventory item.
        '''
        return [self.edition, self.foiling, self.identifier, self.rarity]

    def to_str(self) -> str:
        '''
        Computes the string representation of the inventory item.

        This is a string of the form:

        ```
        {edition}-{identifier}-{rarity}-{foiling}
        ```

        Returns:
          The string representation of the inventory item.
        '''
        return f'{self.edition}-{self.identifier}-{self.rarity}-{self.foiling}'

    def to_tuple(self) -> tuple[str, str, str, str]:
        '''
        Converts this inventory item into a tuple of field strings.

        Returns:
          A `tuple` representation of the inventory item.
        '''
        return (self.edition, self.foiling, self.identifier, self.rarity)

class CardInventory(UserDict):
    '''
    Represents an inventory of unique Flesh and Blood cards.

    This is essentially a `dict[InventoryItem, int]`, where the value of a
    particular key denotes the number of copies in the inventory.

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
      data: The underlying `dict` of `InventoryItem` objects.
    '''
    data: dict[InventoryItem, int]

    def add(
        self,
        identifier: str,
        rarity: str,
        foiling: str,
        count: int = 1,
        edition: str = 'U',
    ) -> None:
        '''
        Adds one or more copies of a unique card to this inventory.

        This method builds a `InventoryItem` object from the specified
        parameters. To add a pre-built `InventoryItem` object to the collection,
        use `add_item()`. If the inventory already contains the specified card,
        its count is increased by the value specified (to set the count, use
        `set()`).

        Args:
          count: The number of copies to add to the inventory.
          edition: The edition code of the card (see `meta.EDITIONS`).
          foiling: The foiling code of the card (see `meta.FOILINGS`).
          identifier: The identifier of the card to add.
          rarity: The rarity code of the card (see `meta.RARITIES`).
        '''
        if not edition in EDITIONS:
            raise ValueError(f'specified card edition code not one of {list(EDITIONS.keys())}')
        if not foiling in FOILINGS:
            raise ValueError(f'specified card foiling code not one of {list(FOILINGS.keys())}')
        if not rarity in RARITIES:
            raise ValueError(f'specified card rarity code not one of {list(RARITIES.keys())}')
        self.add_item(
            item = InventoryItem(
              identifier = identifier,
              rarity = rarity,
              edition = edition,
              foiling = foiling
            ),
            count = count
        )

    def add_item(self, item: InventoryItem, count: int = 1) -> None:
        '''
        Adds one or more copies of a card inventory item to this inventory.

        If the inventory already contains the specified item, its count is
        increased by the value specified (to set the count, use `set_item()`).

        Args:
          item: The card inventory item to add.
          count: The number of copies to add to the inventory.
        '''
        if count <= 0:
            raise ValueError('specified count is not a positive integer value')
        if not item in self:
            self[item] = count
        else:
            self[item] += count

    def count(self) -> int:
        '''
        Computes the total number of cards in this inventory.

        Return:
          The total number of cards in the inventory.
        '''
        return sum(self.data.values())

    def edition_counts(self) -> dict[str, int]:
        '''
        Returns the counts of each edition code contained in this card inventory.

        Returns:
          A `dict` representing the counts of each edition code contained in the inventory.
        '''
        res = {}
        for k, v in self.data.items():
            if k.edition in res:
                res[k.edition] += v
            else:
                res[k.edition] = v
        return res

    def editions(self) -> list[str]:
        '''
        Returns the set of edition codes contained in this card inventory.

        Returns:
          A unique `list` of all card set edition codes contained in the card inventory.
        '''
        res = []
        for i in self.data.keys():
            res.append(i.edition)
        return list(set(res))

    def foiling_counts(self) -> dict[str, int]:
        '''
        Returns the counts of each foiling code contained in this card inventory.

        Returns:
          A `dict` representing the counts of each foiling code contained in the inventory.
        '''
        res = {}
        for k, v in self.data.items():
            if k.foiling in res:
                res[k.foiling] += v
            else:
                res[k.foiling] = v
        return res

    def foilings(self) -> list[str]:
        '''
        Returns the set of foiling codes contained in this card inventory.

        Returns:
          A unique `list` of all card set foiling codes contained in the card inventory.
        '''
        res = []
        for i in self.data.keys():
            res.append(i.foiling)
        return list(set(res))

    @staticmethod
    def from_dict(data: dict[str, int]) -> CardInventory:
        '''
        Parses a new card inventory from the specified `dict` representation.

        Args:
          data: The `dict` representation to parse.

        Returns:
          A new `CardInventory` from the parsed data.
        '''
        res = {}
        for k, v in data.items():
            res[InventoryItem.from_str(k)] = v
        return CardInventory(res)

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

    def identifier_counts(self) -> dict[str, int]:
        '''
        Returns the counts of each identifier contained in this card inventory.

        Returns:
          A `dict` representing the counts of each identifier contained in the inventory.
        '''
        res = {}
        for k, v in self.data.items():
            if k.identifier in res:
                res[k.identifier] += v
            else:
                res[k.identifier] = v
        return res

    def identifiers(self) -> list[str]:
        '''
        Returns the set of identifiers contained in this card inventory.

        Returns:
          A unique `list` of all card set identifiers contained in the card inventory.
        '''
        res = []
        for i in self.data.keys():
            res.append(i.identifier)
        return list(set(res))

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

    def lookup(
        self,
        edition: Optional[str] = None,
        foiling: Optional[str] = None,
        identifier: Optional[str] = None,
        rarity: Optional[str] = None,
        set: Optional[str] = None
    ) -> CardInventory:
        '''
        Returns a subset of the card inventory based on the specified search parameters.

        This is akin to filtering the inventory. Any arguments with `None`
        values are ignored.

        Args:
          edition: The edition code of cards to include in the result.
          foiling: The foiling code of cards to include in the result.
          identifier: The identifier of cards to include in the result.
          rarity: The rarity of cards to include in the result.
          set: The card set code of cards to include in the result.

        Returns:
          A subset of the inventory filtered by the specified arguments.
        '''
        res = {}
        for k, v in self.data.items():
            if not edition is None and not k.edition == edition: continue
            if not foiling is None and not k.foiling == foiling: continue
            if not identifier is None and not k.identifier == identifier: continue
            if not rarity is None and not k.rarity == rarity: continue
            if not set is None and not k.identifier.startswith(set): continue
            res[k] = v
        return CardInventory(res)

    def rarities(self) -> list[str]:
        '''
        Returns the set of rarity codes contained in this card inventory.

        Returns:
          A unique `list` of all card set rarity codes contained in the card inventory.
        '''
        res = []
        for i in self.data.keys():
            res.append(i.rarity)
        return list(set(res))

    def rarity_counts(self) -> dict[str, int]:
        '''
        Returns the counts of each rarity code contained in this card inventory.

        Returns:
          A `dict` representing the counts of each rarity code contained in the inventory.
        '''
        res = {}
        for k, v in self.data.items():
            if k.rarity in res:
                res[k.rarity] += v
            else:
                res[k.rarity] = v
        return res

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
        count: int = 1,
        edition: str = 'U',
    ) -> None:
        '''
        Sets the number of copies associated with a unique card.

        This method builds a `InventoryItem` object from the specified
        parameters. To set a pre-built `InventoryItem` object in the collection,
        use `set_item()`. To add to the current count associated with an item,
        use `add()`.

        Note:
          Setting a card's count to `0` does not delete the item from the
          inventory but rather simply sets the count to `0`. This is useful for
          tracking when you _used_ to own a card, or when _plan_ to obtain a
          copy of a particular card.

        Args:
          count: The number of copies to set the inventory count to.
          edition: The edition code of the card (see `meta.EDITIONS`).
          foiling: The foiling code of the card (see `meta.FOILINGS`).
          identifier: The identifier of the card.
          rarity: The rarity code of the card (see `meta.RARITIES`).
        '''
        if not edition in EDITIONS:
            raise ValueError(f'specified card edition code not one of {list(EDITIONS.keys())}')
        if not foiling in FOILINGS:
            raise ValueError(f'specified card foiling code not one of {list(FOILINGS.keys())}')
        if not rarity in RARITIES:
            raise ValueError(f'specified card rarity code not one of {list(RARITIES.keys())}')
        self.set_item(
            item = InventoryItem(
              identifier = identifier,
              rarity = rarity,
              edition = edition,
              foiling = foiling
            ),
            count = count
        )

    def set_item(self, item: InventoryItem, count: int = 1) -> None:
        '''
        Sets the number of copies of a card inventory item in this inventory.

        If the inventory already contains the specified item, its count is
        increased by the value specified (to set the count, use `set_item()`).

        Note:
          Setting a card's count to `0` does not delete the item from the
          inventory but rather simply sets the count to `0`. This is useful for
          tracking when you _used_ to own a card, or when _plan_ to obtain a
          copy of a particular card.

        Args:
          item: The card inventory item.
          count: The number of copies to set.
        '''
        if count < 0:
            raise ValueError('specified count is not zero or a positive integer value')
        self[item] = count

    def to_cardlist(self, catalog: Optional[CardList] = None) -> CardList:
        '''
        Converts this unique card inventory into a list of generic
        representations of cards.

        Note:
          To instantiate the card list this way, a card catalog (`CardList`)
          must be provided, defaulting to `card.CARD_CATALOG`.

        Args:
          catalog: The card catalog to use as a reference, defaulting to `card.CARD_CATALOG` if `None`.

        Returns:
          A `CardList` object containing the generic represenations of the cards contained within this inventory.
        '''
        cards = []
        for k, v in self.data.items():
            for _ in range(0, v):
                cards.append(k.to_card(catalog=catalog))
        return CardList(cards)

    def to_dict(self) -> dict[str, int]:
        '''
        Converts the inventory object into a raw dictionary of python
        primitives.

        Returns:
          A raw `dict` representation of the card inventory.
        '''
        data = {}
        for k, v in self.data.items():
            data[k.to_str()] = v
        return data

    def to_json(self) -> str:
        '''
        Computes the JSON string representation of the inventory.

        Returns:
          The JSON string representation of the card inventory.
        '''
        return json.dumps(self.to_dict(), indent=JSON_INDENT)
