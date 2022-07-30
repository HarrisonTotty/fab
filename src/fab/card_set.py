'''
Contains the definition of a Flesh and Blood card set.
'''

from __future__ import annotations

import copy
import dataclasses
import datetime
import json

from typing import Any, Optional

DATE_FORMAT = '%Y/%m/%d'
JSON_INDENT: Optional[int] = 2


def _parse_date(datestr: Optional[str]) -> Optional[datetime.date]:
    '''
    A helper function for parsing card set date strings.
    '''
    if datestr is None or not datestr: return None
    return datetime.datetime.strptime(datestr, DATE_FORMAT).date()

def _unparse_date(date: Optional[datetime.date]) -> Optional[str]:
    '''
    A helper function for converting card set dates into their string
    representations.
    '''
    if date is None: return None
    return date.strftime(DATE_FORMAT)


@dataclasses.dataclass
class CardSet:
    '''
    Represents a Flesh and Blood card set.

    The `dates` dictionary maps edition code strings to tuples of the form
    `(<release date>, <out-of-print date>)`, where either tuple value may also
    be `None` if unknown or not applicable.

    Attributes:
      dates: A dictionary correlating the initial release and out-of-print dates for a particular edition.
      editions: The list of editions (by code) the set was printed for.
      id_range: The first and last card identifiers associated with the set.
      identifier: The string shorthand identifier of the set.
      name: The full name of the set.
      urls: A dictionary of relevant upstream URLs associated with each edition of the set.
    '''

    dates: dict[str, tuple[Optional[datetime.date], Optional[datetime.date]]]
    editions: list[str]
    identifier: str
    id_range: tuple[Optional[str], Optional[str]]
    name: str
    urls: dict[str, dict[str, Optional[str]]]

    def __getitem__(self, key: str) -> dict | list | tuple | str:
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
    def from_dict(jsondict: dict[str, Any]) -> CardSet:
        '''
        Creates a new card set from a dictionary object containing unparsed
        date strings.

        Args:
          jsondict: A raw `dict` object representing a card set.

        Returns:
          A new `CardSet` object.
        '''
        rep = copy.deepcopy(jsondict)
        rep['id_range'] = tuple(rep['id_range'])
        for edition, drange in rep['dates'].items():
            rep['dates'][edition] = (_parse_date(drange[0]), _parse_date(drange[1]))
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
        return CardSet.from_dict(json.loads(jsonstr))

    def to_dict(self) -> dict:
        '''
        Converts the card set into a primitive dictionary representation.

        Returns:
          A raw `dict` representing the card set.
        '''
        rep = copy.deepcopy(self.__dict__)
        rep['id_range'] = list(rep['id_range'])
        for edition, drange in rep['dates'].items():
            rep['dates'][edition] = [_unparse_date(drange[0]), _unparse_date(drange[1])]
        return rep

    def to_json(self) -> str:
        '''
        Converts this card set into a JSON string representation.

        Returns:
          The JSON string representation of the set.
        '''
        return json.dumps(self.to_dict(), indent=JSON_INDENT)
