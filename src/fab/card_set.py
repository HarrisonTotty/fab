'''
Contains the definition of a Flesh and Blood card set.
'''

from __future__ import annotations

import copy
import csv
import dataclasses
import datetime
import io
import json
import os

from collections import UserDict
from pandas import DataFrame
from typing import Any, Optional

from IPython.utils.text import indent

from .card import Card

CARD_SET_CATALOG: Optional[CardSetCollection] = None
DATE_FORMAT = '%Y/%m/%d'
JSON_INDENT: Optional[int] = 2

@dataclasses.dataclass
class CardSet:
    '''
    Represents a Flesh and Blood card set. Each card set has the following
    fields:

    Attributes:
      editions: The list of editions the set was printed for.
      identifier: The string shorthand identifier of the set.
      name: The full name of the set.
      release_date: The release date of the card set (if applicable).
    '''

    editions: list[str]
    identifier: str
    name: str
    release_date: Optional[datetime.date]

    def __getitem__(self, key: str) -> Any:
        '''
        Allows one to access fields of a card set via dictionary syntax.

        Args:
          key: The `str` corresponding to the name of the `CardSet` field to access.

        Returns:
          The value of the associated `CardSet` field.
        '''
        return self.__dict__[key]

    def __hash__(self) -> Any:
        '''
        Returns the hash representation of the card set.

        Returns:
          The hash representation of the card set.
        '''
        return hash((self.identifier, self.name))

    def __str__(self) -> str:
        '''
        Returns the string representation of the card set.

        This is an alias of the `CardSet.to_json()` method.

        Returns:
          The JSON string representation of the card set.
        '''
        return self.to_json()

    def keys(self) -> list[str]:
        '''
        Returns the dictionary keys associated with this card set class.

        Returns:
          A `list` of dictionary keys associated with the fields of the set.
        '''
        return list(self.__dict__.keys())

    @staticmethod
    def from_datestr_dict(jsondict: dict[str, Any]) -> CardSet:
        '''
        Creates a new card set from a dictionary object containing unparsed
        date strings.

        Args:
          jsondict: A raw `dict` object representing a card set.

        Returns:
          A new `CardSet` object.
        '''
        rep = copy.deepcopy(jsondict)
        if not rep['release_date'] is None:
            rep['release_date'] = datetime.datetime.strptime(rep['release_date'], DATE_FORMAT).date()
        return CardSet(**rep)

    @staticmethod
    def from_json(jsonstr: str) -> CardSet:
        '''
        Creates a new card set from the specified JSON string.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `CardSet` object from the parsed data.
        '''
        return CardSet.from_datestr_dict(json.loads(jsonstr))

    def to_datestr_dict(self) -> dict:
        '''
        Converts the card set into a dictionary where the `release_date` field
        is set to its string representation.

        Returns:
          A raw `dict` representing the card set.
        '''
        rep = copy.deepcopy(self.__dict__)
        if not rep['release_date'] is None:
            rep['release_date'] = rep['release_date'].strftime(DATE_FORMAT)
        return rep

    def to_json(self) -> str:
        '''
        Converts this card set into a JSON string representation.

        Returns:
          The JSON string representation of the set.
        '''
        return json.dumps(self.to_datestr_dict(), indent=JSON_INDENT)


class CardSetCollection(UserDict):
    '''
    Represents a collection of card sets, stored by identifier.

    Note:
      This class inherits `collections.UserDict`, and thus supports any common
      `dict` methods.

    Attributes:
      data (dict[str, CardSet]): The mapping of `str` identifiers to `CardSet` objects.
    '''

    def editions(self) -> list[str]:
        '''
        Returns the set of all card set editions within this card set
        collection.

        Returns:
          A unique `list` of all card set editions within the set collection.
        '''
        res = []
        for cs in self.data.values():
            res.extend(cs.editions)
        return list(set(res))

    @staticmethod
    def from_csv(csvstr: str, delimiter: str = '\t') -> CardSetCollection:
        '''
        Creates a new card set collection given a CSV string representation.

        Args:
          csvstr: The CSV string representation to parse.
          delimiter: An optional `csv.DictReader` delimiter to use when parsing.

        Returns:
          A new `CardSetCollection` from the parsed data.
        '''
        try:
            csv_data = csv.DictReader(io.StringIO(csvstr), delimiter = delimiter)
        except Exception as e:
            raise Exception(f'unable to parse CSV content - {e}')
        def parse_release_date(inputstr: str) -> str:
            '''
            A helper function for parsing the release date string.
            '''
            if not inputstr or inputstr == 'null': return ''
            if ',' in inputstr:
                return inputstr.split(',')[0].split('T')[0].strip()
            else:
                return inputstr.split('T')[0].strip()
        card_sets = {}
        for entry in csv_data:
            identifier = entry['Identifier'].strip()
            release_date_str = parse_release_date(entry['Initial Release Dates'])
            card_sets[identifier] = CardSet(
                editions = [x.strip() for x in entry['Editions'].split(',')] if entry['Editions'] else [],
                identifier = identifier,
                name = entry['Name'].strip(),
                release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d').date() if release_date_str else None
            )
        return CardSetCollection(card_sets)

    @staticmethod
    def from_json(jsonstr: str) -> CardSetCollection:
        '''
        Creates a new card set collection given a JSON string representation.

        Args:
          jsonstr: The JSON string representation to parse.

        Returns:
          A new `CardSetCollection` from the parsed data.
        '''
        new_items = {}
        for k, v in json.loads(jsonstr).items():
            new_items[k] = CardSet.from_datestr_dict(v)
        return CardSetCollection(new_items)

    def get_release_date(self, card: Card) -> Optional[datetime.date]:
        '''
        Returns the release date for the specified card by looking up its card
        set(s).

        Note:
          The earliest date will be returned for cards released more than once.
          This method returns `None` if no release date is found.

        Args:
          card: The card to obtain the release date of.

        Returns:
          The release date of the specified card, or `None` if not found.
        '''
        if len(self.data) < 1: return None
        release_dates = [s.release_date for i, s in self.data.items() if i in card.sets and not s.release_date is None]
        if release_dates:
            return sorted(release_dates)[0]
        else:
            return None

    def identifiers(self) -> list[str]:
        '''
        Returns the set of all card set identifiers within this card set
        collection.

        Returns:
          The unique `list` of all card set identifiers within the collection.
        '''
        return list(self.data.keys())

    @staticmethod
    def load(file_path: str, set_catalog: bool = False) -> CardSetCollection:
        '''
        Loads a card set collection from the specified `.json` or `.csv` file.

        Note:
          If `set_catalog` is set to `True`, then a cop of the card set
          collection will be set as the default `card_set.CATALOG`.

        Args:
          file_path: The file path from which to load the card set collection.
          set_catalog: Whether to set the loaded data as the default card set catalog.

        Returns:
          A new `CardSetCollection` from the loaded data.
        '''
        with open(os.path.expanduser(file_path), 'r') as f:
            if file_path.endswith('.json'):
                res = CardSetCollection.from_json(f.read())
            elif file_path.endswith('.csv'):
                res = CardSetCollection.from_csv(f.read())
            else:
                raise Exception('specified file is not a CSV or JSON file')
        if set_catalog:
            global CARD_SET_CATALOG
            CARD_SET_CATALOG = res
        return res

    def names(self) -> list[str]:
        '''
        Returns the set of all card set names within this card set collection.

        Returns:
          A unique `list` of all card set names within the collection.
        '''
        return list(set([cs.name for cs in self.data.values()]))

    def release_dates(self) -> list[datetime.date]:
        '''
        Returns the set of all card set release dates within this card set
        collection.

        Returns:
          A unique `list` of all card set release dates within the collection.
        '''
        return sorted(list(set(
            [cs.release_date for cs in self.data.values() if not cs.release_date is None]
        )))

    def save(self, file_path: str):
        '''
        Saves the card set collection to the specified file path.

        Args:
          file_path: The file path to save to.
        '''
        with open(os.path.expanduser(file_path), 'w') as f:
            if file_path.endswith('.json'):
                f.write(self.to_json())
            else:
                raise Exception('specified file path is not a JSON file')

    def to_dataframe(self) -> DataFrame:
        '''
        Converts the list of card sets into a [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

        Returns:
          A pandas `DataFrame` object representing the list of card sets.
        '''
        return DataFrame(self.data)

    def to_json(self) -> str:
        '''
        Computes the JSON string representation of this collection of card sets.

        Returns:
          The JSON string representation of the collection.
        '''
        new_items = {}
        for k, v in self.data.items():
            new_items[k] = v.to_datestr_dict()
        return json.dumps(new_items, indent=JSON_INDENT)
