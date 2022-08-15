'''
Contains the definition of Flesh and Blood card lists.
'''

from __future__ import annotations

import copy
import datetime
import json
import os
import random

from collections import UserList
from pandas import DataFrame
from statistics import mean, median, mode, stdev
from typing import Any, cast, Optional

from .card import Card, STRING_FIELDS, STRING_LIST_FIELDS, VALUE_FIELDS
from .meta import ART_TYPES, FOILINGS, GAME_FORMATS, RARITIES

JSON_INDENT: Optional[int] = 2

def _sort_list_field(field: str, values: list[int | str], reverse: bool = False) -> list[int | str]:
    '''
    A helper function for sorting certain `list[str]` fields of cards.
    '''
    if field == 'art_types':
        return sorted(values, key=lambda x: list(ART_TYPES.keys()).index(x), reverse=reverse)
    elif field == 'foilings':
        return sorted(values, key=lambda x: list(FOILINGS.keys()).index(x), reverse=reverse)
    elif field == 'rarities':
        return sorted(values, key=lambda x: list(RARITIES.keys()).index(x), reverse=reverse)
    else:
        return sorted(values)

class CardList(UserList[Card]):
    '''
    Represents a collection of cards.

    Note:
      This is ultimately a superclass of `list`, and thus supports all common
      `list` methods.

    Attributes:
      data: The raw `list` of `Card` objects contained within the object.
    '''
    data: list[Card]

    def ability_keywords(self) -> list[str]:
        '''
        Returns the set of all ability keywords in this card list.

        Returns:
          The unique `list` of all ability keywords within the card list.
        '''
        return cast(list[str], self.collect_unique('ability_keywords'))

    def actions(self) -> CardList:
        '''
        Returns the set of all action cards in this card list.

        Returns:
          The set of all action cards in the card list.
        '''
        return CardList(card for card in self.data if card.is_action())

    def art_types(self) -> list[str]:
        '''
        Returns the set of all art type codes in this card list.

        Returns:
          The unique `list` of all art type codes within the card list.
        '''
        return cast(list[str], self.collect_unique('art_types'))

    def attacks(self) -> CardList:
        '''
        Returns the set of all attack cards in this card list.

        Returns:
          The set of all attack cards in the card list.
        '''
        return CardList(card for card in self.data if card.is_attack())

    def attack_reactions(self) -> CardList:
        '''
        Returns the set of all attack reaction cards in this card list.

        Returns:
          The set of all attack reaction cards in the card list.
        '''
        return CardList(card for card in self.data if card.is_attack_reaction())

    def auras(self) -> CardList:
        '''
        Returns the set of all aura cards in this card list.

        Returns:
          The set of all aura cards in the card list.
        '''
        return CardList(card for card in self.data if card.is_aura())

    def card_types(self) -> list[str]:
        '''
        Returns the set of all primary card types in this card list.

        Returns:
          The unique `list` of all primary card types within the card list.
        '''
        return cast(list[str], self.collect_unique('card_type'))

    def class_types(self) -> list[str]:
        '''
        Returns the set of all hero class types in this card list.

        Returns:
          The unique `list` of all hero class types within the card list.
        '''
        return cast(list[str], self.collect_unique('class_type'))

    def collect(self, field: str, reverse: bool = False, sort: bool = True) -> list[int | str]:
        '''
        Returns the list of all `Card` field values associated with the
        specified `Card` field in this list of cards.

        Warning:
          Note that values of `None` and `str` values for `int`-based fields
          will be excluded. The card field `legality` may not be collected.

        Args:
          field: The name of the `Card` field to collect (such as `cost`).
          reverse: Whether to reverse the sort order if `sort` is `True`.
          sort: Whether to sort the results.
        '''
        if field in STRING_FIELDS:
            result = [card[field] for card in self.data if isinstance(card[field], str)]
        elif field in STRING_LIST_FIELDS:
            result = []
            for card in self.data:
                result.extend(card[field]) # type: ignore
        elif field in VALUE_FIELDS:
            result = [card[field] for card in self.data if isinstance(card[field], int)]
        else:
            raise Exception(f'unsupported collection field "{field}"')
        result = cast(list[int | str], result)
        return _sort_list_field(field, result, reverse=reverse) if sort else result

    def collect_unique(self, field: str, reverse: bool = False, sort: bool = True) -> list[int | str]:
        '''
        Returns the set of all unique `Card` field values associated with the
        specified `Card` field in this list of cards.

        Warning:
          Note that values of `None` and `str` values for `int`-based fields
          will be excluded. The card field `legality` may not be collected.

        Args:
          field: The name of the `Card` field to collect (such as `cost`).
          reverse: Whether to reverse the sort order if `sort` is `True`.
          sort: Whether to sort the results.
        '''
        unique = list(set(self.collect(field, sort=False)))
        return _sort_list_field(field, unique, reverse=reverse) if sort else unique

    def costs(self) -> list[int]:
        '''
        Returns the set of all card costs associated with this list of cards.

        Warning:
          This excludes cards with no cost or with variable cost.

        Returns:
          The set of all card costs in the card list.
        '''
        return cast(list[int], self.collect_unique('cost'))

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

    def dates(self) -> dict[str, tuple[Optional[datetime.date], Optional[datetime.date]]]:
        '''
        Returns the combined `dates` field of all cards in the list.

        Returns:
          A mapping of all card variations to their corresponding release and/or out-of-print dates.
        '''
        result = {}
        for card in self.data:
            for k, v in card.dates.items():
                if not k in result:
                    result[k] = v
        return copy.deepcopy(result)

    def defense_reactions(self) -> CardList:
        '''
        Returns the set of all defense reaction cards in this card list.

        Returns:
          The set of all defense reaction cards in the card list.
        '''
        return CardList(card for card in self.data if card.is_defense_reaction())

    def defense_values(self) -> list[int]:
        '''
        Returns the set of all card defense values associated with this list of
        cards.

        Warning:
          This excludes cards with no defense or with variable defense.

        Returns:
          A unique `list` of card defense values associated with the list of cards.
        '''
        return cast(list[int], self.collect_unique('defense'))

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

    def editions(self) -> list[str]:
        '''
        Returns the set of all set editions in this card list.

        Returns:
          The unique `list` of all set editions within the card list.
        '''
        return cast(list[str], self.collect_unique('editions'))

    def effect_keywords(self) -> list[str]:
        '''
        Returns the set of all effect keywords in this card list.

        Returns:
          The unique `list` of all effect keywords within the card list.
        '''
        return cast(list[str], self.collect_unique('effect_keywords'))

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
        return CardList(card for card in self.data if card.is_equipment())

    def filter(self, **kwargs: Any) -> CardList:
        '''
        Filters the list of cards against one or more `Card` fields.

        In addition to functions/lambdas, you can also specify:

        * A value of `None` for any `Card` field of type `Optional` (such as
          `body`).
        * A `str` for any `Card` field of type `str` or `Optional[str]` (such as
          `type_text`). These comparisons are case-insensitive and will match
          substrings.
        * An `int` for any value-based `Card` field (such as `cost`).
        * A `tuple[int, int]` for any value-based `Card` field (such as `cost`),
          defining a range of integer values to include (inclusive).
        * A `list[str]` for any `Card` field of type `list[str]` (such as
          `types`). At least one value of the specified list must be present for
          a card to be included.
        * A `str` for any `Card` field of type `list[str]` (such as `types`).
          This is the same as passing in a single-element list to the argument.
        * A value of `None` for any `Card` field of type `list[str]` (such as
          `types`). This is the same thing as passing an empty list.
        * A `str` for the `legality` keyword argument, corresponding to a format
          code that the card must be legal in to be included.
        * A `str` of the form `YYYY`, `YYYY/MM`, or `YYYY/MM/DD` for the `dates`
          keyword argument, corresponding to only including cards with an
          _initial release date_ in the same year and/or month and/or day as the
          specified string (for example: `2022/08`).
        * A `datetime.date` for the `dates` keyword argument, corresponding to
          only including cards with the same _initial release date_ as the
          specified value.
        * A `bool` value to a keyword argument called `negate`, which defines
          whether to negate the filter query.

        Warning:
          When filtering cards by type to discern which cards may be used in a
          deck, be mindful that when invoking this method with something like
          `types=['Generic', 'Shadow', 'Runeblade']`, your result includes cards
          which contain the _Generic_, _Shadow_, **or** _Runeblade_ types (it
          will also contain _Shadow Brute_ cards, for instance). When you want
          to filter cards by types which work with a particular hero, it's best
          to leverage `Deck` objects instead.

        Example:
          The following examples assume `cards` is an existing `CardList`
          object.

          Return all cards which contain the _Attack_ type:

          ```python
          # Method 1 - Lambda Expressions
          result = cards.filter(types=lambda t: 'Attack' in t)

          # Method 2 - List Shortcut
          result = cards.filter(types=['Attack'])

          # Method 3 - String Shortcut (Preferred)
          result = cards.filter(types='Attack')
          ```

          Return all _Brute or Illusionist_ cards with 7 power:

          ```python
          result = cards.filter(types=['Brute', 'Illusionist'], power=7)
          ```

          Return all _Illusionist_ cards that don't pitch for 3 resources:

          ```python
          result = cards.filter(types='Illusionist').filter(pitch=3, negate=True)
          ```

        Returns:
          A new `CardList` containing the `Card` objects that meet the filtering requirements.
        '''
        if not self.data: return self
        filtered: list[Card] = []
        negate = kwargs['negate'] if 'negate' in kwargs else False
        for card in self.data:
            add = True
            for arg, value in kwargs.items():
                if arg == 'negate':
                    continue
                elif arg in STRING_FIELDS:
                    cardv = cast(Optional[str], card[arg])
                    if value is None:
                        if negate:
                            if cardv is None:
                                add = False
                                break
                        else:
                            if not cardv is None:
                                add = False
                                break
                    elif isinstance(value, str):
                        if negate:
                            if isinstance(cardv, str) and value.lower() in cardv.lower():
                                add = False
                                break
                        else:
                            if not isinstance(cardv, str) or not value.lower() in cardv.lower():
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg in STRING_LIST_FIELDS:
                    cardv = cast(list[str], card[arg])
                    if value is None:
                        if negate:
                            if not cardv:
                                add = False
                                break
                        else:
                            if cardv:
                                add = False
                                break
                    elif isinstance(value, list):
                        if negate:
                            if any(v in cardv for v in value):
                                add = False
                                break
                        else:
                            if not any(v in cardv for v in value):
                                add = False
                                break
                    elif isinstance(value, str):
                        if negate:
                            if value in cardv:
                                add = False
                                break
                        else:
                            if not value in cardv:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg in VALUE_FIELDS:
                    cardv = cast(Optional[int | str], card[arg])
                    if value is None:
                        if negate:
                            if cardv is None:
                                add = False
                                break
                        else:
                            if not cardv is None:
                                add = False
                                break
                    elif isinstance(value, int):
                        if negate:
                            if isinstance(cardv, int) and cardv == value:
                                add = False
                                break
                        else:
                            if not isinstance(cardv, int) or cardv != value:
                                add = False
                                break
                    elif isinstance(value, tuple):
                        if negate:
                            if isinstance(cardv, int) and cardv >= value[0] and cardv <= value[1]:
                                add = False
                                break
                        else:
                            if not isinstance(cardv, int) or cardv < value[0] or cardv > value[1]:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg == 'dates':
                    ird = card.initial_release_date()
                    if isinstance(value, str):
                        if not value.isdigit() and not '/' in value:
                            raise ValueError('dates specification not of the form "YYYY", "YYYY/MM", or "YYYY/MM/DD"')
                        chunks = [int(c) for c in value.split('/')]
                        while len(chunks) < 3: chunks.append(None)
                        [year, month, day] = chunks
                        if not day is None:
                            if negate:
                                if not ird is None and ird.year == year and ird.month == month and ird.day == day:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year or ird.month != month or ird.day != day:
                                    add = False
                                    break
                        elif not month is None:
                            if negate:
                                if not ird is None and ird.year == year and ird.month == month:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year or ird.month != month:
                                    add = False
                                    break
                        else:
                            if negate:
                                if not ird is None and ird.year == year:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year:
                                    add = False
                                    break
                    elif isinstance(value, datetime.date):
                        if negate:
                            if value == ird:
                                add = False
                                break
                        else:
                            if value != ird:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(card.dates):
                                add = False
                                break
                        else:
                            if not value(card.dates):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg == 'legality':
                    cardv = cast(dict[str, bool], card[arg])
                    if isinstance(value, str):
                        if negate:
                            if card.is_legal(value):
                                add = False
                                break
                        else:
                            if not card.is_legal(value):
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                else:
                    raise Exception(f'unknown filtering argument "{arg}"')
            if add: filtered.append(card)
        return CardList(filtered)

    def filter_exact(self, **kwargs: Any) -> CardList:
        '''
        Filters the list of cards against one or more `Card` fields.

        This method is similar to `filter()` except that when specifying a
        `list[str]` for those fields that support it, _all_ elements must
        be present for the card to be included in the result. However, passing
        just a `str` to those fields acts the same as in `filter()`.

        Example:
          The following examples assume `cards` is an existing `CardList`
          object.

          Return all _Shadow Runeblade Action_ cards:

          ```python
          result = cards.filter_exact(types=['Shadow', 'Runeblade', 'Action'])
          ```

        Returns:
          A new `CardList` containing the `Card` objects that meet the filtering requirements.
        '''
        if not self.data: return self
        filtered: list[Card] = []
        negate = kwargs['negate'] if 'negate' in kwargs else False
        for card in self.data:
            add = True
            for arg, value in kwargs.items():
                if arg == 'negate':
                    continue
                elif arg in STRING_FIELDS:
                    cardv = cast(Optional[str], card[arg])
                    if value is None:
                        if negate:
                            if cardv is None:
                                add = False
                                break
                        else:
                            if not cardv is None:
                                add = False
                                break
                    elif isinstance(value, str):
                        if negate:
                            if isinstance(cardv, str) and value.lower() in cardv.lower():
                                add = False
                                break
                        else:
                            if not isinstance(cardv, str) or not value.lower() in cardv.lower():
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg in STRING_LIST_FIELDS:
                    cardv = cast(list[str], card[arg])
                    if value is None:
                        if negate:
                            if not cardv:
                                add = False
                                break
                        else:
                            if cardv:
                                add = False
                                break
                    elif isinstance(value, list):
                        if negate:
                            if set(value) == set(cardv):
                                add = False
                                break
                        else:
                            if set(value) != set(cardv):
                                add = False
                                break
                    elif isinstance(value, str):
                        if negate:
                            if value in cardv:
                                add = False
                                break
                        else:
                            if not value in cardv:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg in VALUE_FIELDS:
                    cardv = cast(Optional[int | str], card[arg])
                    if value is None:
                        if negate:
                            if cardv is None:
                                add = False
                                break
                        else:
                            if not cardv is None:
                                add = False
                                break
                    elif isinstance(value, int):
                        if negate:
                            if isinstance(cardv, int) and cardv == value:
                                add = False
                                break
                        else:
                            if not isinstance(cardv, int) or cardv != value:
                                add = False
                                break
                    elif isinstance(value, tuple):
                        if negate:
                            if isinstance(cardv, int) and cardv >= value[0] and cardv <= value[1]:
                                add = False
                                break
                        else:
                            if not isinstance(cardv, int) or cardv < value[0] or cardv > value[1]:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg == 'dates':
                    ird = card.initial_release_date()
                    if isinstance(value, str):
                        if not value.isdigit() and not '/' in value:
                            raise ValueError('dates specification not of the form "YYYY", "YYYY/MM", or "YYYY/MM/DD"')
                        chunks = [int(c) for c in value.split('/')]
                        while len(chunks) < 3: chunks.append(None)
                        [year, month, day] = chunks
                        if not day is None:
                            if negate:
                                if not ird is None and ird.year == year and ird.month == month and ird.day == day:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year or ird.month != month or ird.day != day:
                                    add = False
                                    break
                        elif not month is None:
                            if negate:
                                if not ird is None and ird.year == year and ird.month == month:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year or ird.month != month:
                                    add = False
                                    break
                        else:
                            if negate:
                                if not ird is None and ird.year == year:
                                    add = False
                                    break
                            else:
                                if ird is None or ird.year != year:
                                    add = False
                                    break
                    elif isinstance(value, datetime.date):
                        if negate:
                            if value == ird:
                                add = False
                                break
                        else:
                            if value != ird:
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(card.dates):
                                add = False
                                break
                        else:
                            if not value(card.dates):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                elif arg == 'legality':
                    cardv = cast(dict[str, bool], card[arg])
                    if isinstance(value, str):
                        if negate:
                            if card.is_legal(value):
                                add = False
                                break
                        else:
                            if not card.is_legal(value):
                                add = False
                                break
                    elif callable(value):
                        if negate:
                            if value(cardv):
                                add = False
                                break
                        else:
                            if not value(cardv):
                                add = False
                                break
                    else:
                        raise ValueError(f'unsupported value type for "{arg}" argument')
                else:
                    raise Exception(f'unknown filtering argument "{arg}"')
            if add: filtered.append(card)
        return CardList(filtered)

    def foilings(self) -> list[str]:
        '''
        Returns the set of all foilings in this card list.

        Returns:
          The unique `list` of all foilings within the card list.
        '''
        return cast(list[str], self.collect_unique('foilings'))

    @staticmethod
    def from_json(jsonstr: str) -> CardList:
        '''
        Creates a new list of cards given a JSON string representation.

        Args:
          jsonstr: The JSON string representation to parse into a card list.

        Returns:
          A new `CardList` object from the parsed data.
        '''
        return CardList.from_list(json.loads(jsonstr))

    @staticmethod
    def from_list(data: list[dict[str, Any]]) -> CardList:
        '''
        Creates a new list of cards given its raw list representation.

        Args:
          data: The raw list representation of the card list.

        Returns:
          A new `CardList` object from the parsed data.
        '''
        return CardList([Card.from_dict(d) for d in data])

    def full_names(self) -> list[str]:
        '''
        Returns the set of all full card names within this list of cards.

        Returns:
          A unique `list` of all full card names within the list of cards.
        '''
        return cast(list[str], self.collect_unique('full_name'))

    def grants_keywords(self) -> list[str]:
        '''
        Returns the set of all keywords within this list of cards that cards
        grant to other cards.

        Returns:
          A unique `list` of all granted keywords within the list of cards.
        '''
        return cast(list[str], self.collect_unique('grants_keywords'))

    def group(self, by: str = 'types', count_threshold: int = 1, include_none: bool = True) -> dict[Optional[datetime.date | int | str], CardList]:
        '''
        Groups cards by the specified `Card` field.

        The result of the grouping is a dictionary whose keys correspond to
        potential values associated with the specified card field. Fields of
        type `list[str]` are unpacked into their sub-values, and replaced with
        `None` if empty. When grouping by `legality`, the result is the subset
        of all cards currently legal for each format code. Grouping by the
        `dates` field implies grouping by release date.

        Args:
          by: The `Card` field to group by.
          count_threshold: Excludes groups with less than this many elements from the result.
          include_none: Whether to include fields with value `None` in the result.

        Returns:
          A `dict` of `CardList` objects grouped by the specified `Card` field.
        '''
        if not self.data: return {}
        if count_threshold < 1:
            raise ValueError('specified count threshold must be a positive integer value')
        res = {}
        for card in self.data:
            if by in list(STRING_FIELDS.keys()) + list(VALUE_FIELDS.keys()):
                value = cast(Optional[int | str], card[by])
                if not include_none and value is None:
                    continue
                else:
                    if not value in res:
                        res[value] = CardList([card])
                    else:
                        res[value].append(card)
            elif by in STRING_LIST_FIELDS:
                value = cast(list[str], card[by])
                if not value:
                    if not include_none:
                        continue
                    else:
                        if not None in res:
                            res[None] = CardList([card])
                        else:
                            res[None].append(card)
                else:
                    for v in value:
                        if not v in res:
                            res[v] = CardList([card])
                        else:
                            res[v].append(card)
            elif by == 'dates':
                rel_dates = card.release_dates()
                for v in rel_dates.values():
                    if not include_none and v is None:
                        continue
                    else:
                        if not v in res:
                            res[v] = CardList([card])
                        else:
                            res[v].append(card)
            elif by == 'legality':
                for fmt, legality in card.legality:
                    if legality:
                        if not fmt is res:
                            res[fmt] = CardList([card])
                        else:
                            res[fmt].append(card)
            else:
                raise Exception(f'unknown filter group "{by}"')
        return {k: v for k, v in res.items() if len(v) >= count_threshold}

    def heroes(self) -> CardList:
        '''
        Returns the set of all hero cards in this card list.

        Returns:
          The set of all hero cards within the card list.
        '''
        return CardList(card for card in self.data if card.is_hero())

    def identifiers(self) -> list[str]:
        '''
        Returns the set of all card identifiers in this card list.

        Returns:
          The unique `list` of all card identifiers within the card list.
        '''
        return cast(list[str], self.collect_unique('identifiers'))

    def instants(self) -> CardList:
        '''
        Returns the set of all instant cards in this card list.

        Returns:
          The set of all instant cards within the card list.
        '''
        return CardList(card for card in self.data if card.is_instant())

    def intellect_values(self) -> list[int]:
        '''
        Returns the set of all card intellect values associated with this list
        of cards.

        Warning:
          This excludes cards with no intellect or with variable intellect.

        Returns:
          A unique `list` of all card intellect values within the list of cards.
        '''
        return cast(list[int], self.collect_unique('intellect'))

    def item_cards(self) -> CardList:
        '''
        Returns the set of all item cards in this card list.

        Returns:
          The set of all item cards within the list of cards.
        '''
        return CardList(card for card in self.data if card.is_item())

    def keywords(self) -> list[str]:
        '''
        Returns the set of all keywords in this card list.

        Returns:
          A unique `list` of all keywords within the list of cards.
        '''
        return cast(list[str], self.collect_unique('keywords'))

    def label_keywords(self) -> list[str]:
        '''
        Returns the set of all label keywords in this card list.

        Returns:
          The unique `list` of all label keywords within the card list.
        '''
        return cast(list[str], self.collect_unique('label_keywords'))

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
            res[f] = not (False in [card.is_legal(f) for card in self.data if f in card.legality])
        return res

    def life_values(self) -> list[int]:
        '''
        Returns the set of all card life values associated with this list of
        cards.

        Warning:
          This excludes cards with no life value or with variable life value.

        Returns:
          The unique `list` of all card life values within the card list.
        '''
        return cast(list[int], self.collect_unique('life'))

    @staticmethod
    def load(file_path: str) -> CardList:
        '''
        Loads a list of cards from the specified `.json` file.

        Args:
          file_path: The file path to load from.

        Returns:
          A new `CardList` object.
        '''
        if not file_path.endswith('.json'):
            raise Exception('specified file is not a JSON file')
        with open(os.path.expanduser(file_path), 'r') as f:
            return CardList.from_json(f.read())

    def max_cost(self) -> int:
        '''
        Computes the maximum card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Returns:
          The maximum card cost within the list of cards.
        '''
        return cast(int, self.statistic('cost', 'max'))

    def max_defense(self) -> int:
        '''
        Computes the maximum card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Returns:
          The maximum card defense value within the list of cards.
        '''
        return cast(int, self.statistic('defense', 'max'))

    def max_intellect(self) -> int:
        '''
        Computes the maximum card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Returns:
          The maximum card intellect value within the list of cards.
        '''
        return cast(int, self.statistic('intellect', 'max'))

    def max_life(self) -> int:
        '''
        Computes the maximum card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Returns:
          The maximum card life value within the list of cards.
        '''
        return cast(int, self.statistic('life', 'max'))

    def max_pitch(self) -> int:
        '''
        Computes the maximum card pitch value within this card list.

        Warning:
          Cards with variable or no pitch are ignored.

        Returns:
          The maximum card pitch value within this list of cards.
        '''
        return cast(int, self.statistic('pitch', 'max'))

    def max_power(self) -> int:
        '''
        Computes the maximum card attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Returns:
          The maximum card attack power value within this list of cards.
        '''
        return cast(int, self.statistic('power', 'max'))

    def mean_cost(self, precision: int = 2) -> float:
        '''
        Computes the mean card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean card cost of cards in the list.
        '''
        return cast(float, self.statistic('cost', 'mean', precision=precision))

    def mean_defense(self, precision: int = 2) -> float:
        '''
        Computes the mean card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean defense of cards in the list.
        '''
        return cast(float, self.statistic('defense', 'mean', precision=precision))

    def mean_intellect(self, precision: int = 2) -> float:
        '''
        Computes the mean card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean intellect of cards in the list.
        '''
        return cast(float, self.statistic('intellect', 'mean', precision=precision))

    def mean_life(self, precision: int = 2) -> float:
        '''
        Computes the mean card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean life value of cards in the list.
        '''
        return cast(float, self.statistic('life', 'mean', precision=precision))

    def mean_pitch(self, precision: int = 2) -> float:
        '''
        Computes the mean card pitch within this card list.

        Warning:
          Cards with variable or no pitch are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean pitch value of cards in the list.
        '''
        return cast(float, self.statistic('pitch', 'mean', precision=precision))

    def mean_power(self, precision: int = 2) -> float:
        '''
        Computes the mean card attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The mean attack power of cards in the list.
        '''
        return cast(float, self.statistic('power', 'mean', precision=precision))

    def median_cost(self, precision: int = 2) -> float:
        '''
        Computes the median card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median resource cost of cards in the list.
        '''
        return cast(float, self.statistic('cost', 'median', precision=precision))

    def median_defense(self, precision: int = 2) -> float:
        '''
        Computes the median card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median defense value of cards in the list.
        '''
        return cast(float, self.statistic('defense', 'median', precision=precision))

    def median_intellect(self, precision: int = 2) -> float:
        '''
        Computes the median card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median intellect of cards in the list.
        '''
        return cast(float, self.statistic('intellect', 'median', precision=precision))

    def median_life(self, precision: int = 2) -> float:
        '''
        Computes the median card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median life value of cards in the list.
        '''
        return cast(float, self.statistic('life', 'median', precision=precision))

    def median_pitch(self, precision: int = 2) -> float:
        '''
        Computes the median card pitch value within this card list.

        Warning:
          Cards with variable or no pitch value are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median pitch value of cards in the list.
        '''
        return cast(float, self.statistic('pitch', 'median', precision=precision))

    def median_power(self, precision: int = 2) -> float:
        '''
        Computes the median card attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The median attack power of cards in the list.
        '''
        return cast(float, self.statistic('power', 'median', precision=precision))

    def min_cost(self) -> int:
        '''
        Computes the minimum card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Returns:
          The minimum card cost within the list.
        '''
        return cast(int, self.statistic('cost', 'min'))

    def min_defense(self) -> int:
        '''
        Computes the minimum card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Returns:
          The minimum card defense value within the list.
        '''
        return cast(int, self.statistic('defense', 'min'))

    def min_intellect(self) -> int:
        '''
        Computes the minimum card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Returns:
          The minimum intellect in the list.
        '''
        return cast(int, self.statistic('intellect', 'min'))

    def min_life(self) -> int:
        '''
        Computes the minimum card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Returns:
          The minimum card life value in the list.
        '''
        return cast(int, self.statistic('life', 'min'))

    def min_pitch(self) -> int:
        '''
        Computes the minimum card pitch value within this card list.

        Warning:
          Cards with variable or no pitch value are ignored.

        Returns:
          The minimum pitch value in the list.
        '''
        return cast(int, self.statistic('pitch', 'min'))

    def min_power(self) -> int:
        '''
        Computes the minimum attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Returns:
          The minimum attack power in the list.
        '''
        return cast(int, self.statistic('power', 'min'))

    def names(self) -> list[str]:
        '''
        Returns the set of all card names in this card list.

        Returns:
          The unique `list` of card names within the list of cards.
        '''
        return cast(list[str], self.collect_unique('name'))

    def num_blue(self) -> int:
        '''
        Returns the number of "blue" cards (pitch 3) in this card list.

        Returns:
          The number of cards in this card list that pitch for 3 resources.
        '''
        return len(self.filter(color='Blue'))

    def num_red(self) -> int:
        '''
        Returns the number of "red" cards (pitch 1) in this card list.

        Returns:
          The number of cards in this card list that pitch for 1 resource.
        '''
        return len(self.filter(color='Red'))

    def num_yellow(self) -> int:
        '''
        Returns the number of "yellow" cards (pitch 2) in this card list.

        Returns:
          The number of cards in this card list that pitch for 2 resources.
        '''
        return len(self.filter(color='Yellow'))

    def out_of_print_dates(self) -> dict[str, Optional[datetime.date]]:
        '''
        Returns a mapping of all card variations to their out-of-print dates.

        Returns:
          A mapping of card variations to their out-of-print dates.
        '''
        return {k: v[1] for k, v in self.dates().items()}

    def pitch_cost_difference(self) -> int:
        '''
        Returns the difference between the pitch and cost values of all cards.

        Note:
          A positive integer indicates that on average one generates more pitch
          value than consumes it.

        Warning:
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

        Warning:
          This excludes cards with no pitch or with variable pitch.

        Returns:
          The unique `list` of card pitch values within the list of cards.
        '''
        return cast(list[int], self.collect_unique('pitch'))

    def power_defense_difference(self) -> int:
        '''
        Returns the difference between the power and defense values of all
        cards.

        Note:
          A positive integer indicates the deck prefers an offensive strategy.

        Warning:
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

        Warning:
          This excludes cards with no power or with variable power.

        Returns:
          The unique `list` of power values within the list of cards.
        '''
        return cast(list[int], self.collect_unique('power'))

    def rarities(self) -> list[str]:
        '''
        Returns the set of all card rarities in this card list.

        Returns:
          A unique `list` of card rarities in the list of cards.
        '''
        return cast(list[str], self.collect_unique('rarities'))

    def reactions(self) -> CardList:
        '''
        Returns the set of all attack and defense reaction cards in this card
        list.

        Returns:
          A list of all attack and defense reaction cards within the card list.
        '''
        return CardList(card for card in self.data if card.is_reaction())

    def release_dates(self) -> dict[str, Optional[datetime.date]]:
        '''
        Returns a mapping of all card variations to their release dates.

        Returns:
          A mapping of card variations to their release dates.
        '''
        return {k: v[0] for k, v in self.dates().items()}

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

    def sort(self, by: str = 'full_name', reverse: bool = False) -> CardList:
        '''
        Sorts the list of cards, returning a new sorted collection.

        `by` is a string corresponding to the field to sort by (for example:
        `type_text`). Any `None` values will be shifted to the beginning of the
        resulting `CardList`, or at the end if `reverse` is equal to `True`.
        Note that when specifying a field whose value is of type `list[str]`,
        the ordering is based on the _number_ of values within those lists.
        `rarities` is a special case where cards are sorted by their
        highest (if reverse) or lowest rarity value. Sorting by legality is not
        implemented. Sorting by `dates` will always reference the _initial
        release date_ for a card.

        Args:
          by: The `Card` field to sort by.
          reverse: Whether to reverse the sort order.

        Returns:
          A new, sorted `CardList` object.
        '''
        if not self.data: return self
        empty: list[Card] = []
        valued: list[Card] = []
        varied: list[Card] = []
        if by in STRING_FIELDS:
            for card in self.data:
                value = cast(Optional[str], card[by])
                if value is None:
                    empty.append(card)
                else:
                    valued.append(card)
            if reverse:
                return CardList(
                    sorted(valued, key=lambda c: cast(str, c[by]), reverse=reverse) + \
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse)
                )
            else:
                return CardList(
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse) + \
                    sorted(valued, key=lambda c: cast(str, c[by]), reverse=reverse)
                )
        elif by == 'rarities':
            for card in self.data:
                value = cast(list[str], card[by])
                if not value:
                    empty.append(card)
                else:
                    valued.append(card)
            if reverse:
                return CardList(
                    sorted(valued, key=lambda c: cast(int, list(RARITIES.keys()).index(c.lowest_rarity())), reverse=reverse) + \
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse)
                )
            else:
                return CardList(
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse) + \
                    sorted(valued, key=lambda c: cast(int, list(RARITIES.keys()).index(c.highest_rarity())), reverse=reverse)
                )
        elif by in STRING_LIST_FIELDS:
            return CardList(
               sorted(self.data, key=lambda c: len(cast(list[str], c[by])), reverse=reverse)
            )
        elif by in VALUE_FIELDS:
            for card in self.data:
                value = cast(Optional[int | str], card[by])
                if value is None:
                    empty.append(card)
                elif isinstance(value, str):
                    varied.append(card)
                else:
                    valued.append(card)
            if reverse:
                return CardList(
                    sorted(valued, key=lambda c: cast(int, c[by]), reverse=reverse) + \
                    sorted(varied, key=lambda c: c.full_name, reverse=reverse) + \
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse)
                )
            else:
                return CardList(
                    sorted(empty, key=lambda c: c.full_name, reverse=reverse) + \
                    sorted(varied, key=lambda c: c.full_name, reverse=reverse) + \
                    sorted(valued, key=lambda c: cast(int, c[by]), reverse=reverse)
                )
        else:
            raise Exception(f'unsupported sort field "{by}"')

    def sets(self) -> list[str]:
        '''
        Returns the set of all card sets in this list.

        Returns:
          A unique `list` of all card sets within the list of cards.
        '''
        return cast(list[str], self.collect_unique('sets'))

    def shuffle(self) -> None:
        '''
        Shuffles this list of cards in-place.
        '''
        random.shuffle(self.data)

    def statistic(self, field: str, function: str, precision: int = 2) -> float | int:
        '''
        Computes the specified statistical function for the specified `Card`
        field.

        The specified statistic `function` may be `max`, `mean`, `median`,
        `min`, `mode`, `stdev`, or `total`.

        Args:
          field: The `Card` attribute to compute the statistic for (such as `cost`).
          function: The statistical function to compute.
        '''
        int_functions = ['max', 'min', 'mode', 'total']
        float_functions = ['mean', 'median']
        funcmap = {
            'max': max,
            'mean': mean,
            'median': median,
            'min': min,
            'mode': mode,
            'stdev': stdev,
            'total': sum
        }
        if not field in VALUE_FIELDS:
            raise Exception(f'specified card field "{field}" does not exist or is not a value field')
        array = [card[field] for card in self.data if isinstance(card[field], int)]
        if function in int_functions:
            if not array: return 0
        elif function in float_functions:
            if not array: return 0.0
        elif function == 'stdev':
            if len(array) < 2: return 0.0
        else:
            raise Exception(f'unknown statistical function "{function}"')
        if function in int_functions:
            return funcmap[function](array)
        else:
            return round(funcmap[function](array), precision)

    def statistics(self, precision: int = 2) -> dict[str, int | float]:
        '''
        Computes all possible statistics associated with this collection of
        cards.

        Warning:
          Cards with variable or no value for certain fields will be excluded
          from that field's calculations.

        Args:
          precision: Specifies the number of decimal places any `float` result will be rounded to.

        Returns:
          A `dict` containing the results of various statistical functions.
        '''
        result: dict[str, int | float] = { 'count': len(self.data) }
        for function in ['max', 'mean', 'median', 'min', 'mode', 'stdev', 'total']:
            for field in VALUE_FIELDS:
                result[f'{function}_{field}'] = self.statistic(field, function, precision=precision)
        result['num_blue'] = self.num_blue()
        result['num_red'] = self.num_red()
        result['num_yellow'] = self.num_yellow()
        result['pitch_cost_difference'] = self.pitch_cost_difference()
        result['power_defense_difference'] = self.power_defense_difference()
        return result

    def stdev_cost(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of card cost in the list.
        '''
        return cast(float, self.statistic('cost', 'stdev', precision=precision))

    def stdev_defense(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of card defense in the list.
        '''
        return cast(float, self.statistic('defense', 'stdev', precision=precision))

    def stdev_intellect(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of intellect in the list.
        '''
        return cast(float, self.statistic('intellect', 'stdev', precision=precision))

    def stdev_life(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of life value in the list.
        '''
        return cast(float, self.statistic('life', 'stdev', precision=precision))

    def stdev_pitch(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of card pitch value within this card list.

        Warning:
          Cards with variable or no pitch value are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of pitch value in the list.
        '''
        return cast(float, self.statistic('pitch', 'stdev', precision=precision))

    def stdev_power(self, precision: int = 2) -> float:
        '''
        Computes the standard deviation of attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Args:
          precision: Specifies the number of decimal places the result will be rounded to.

        Returns:
          The standard deviation of attack power in the list.
        '''
        return cast(float, self.statistic('power', 'stdev', precision=precision))

    def subtypes(self) -> list[str]:
        '''
        Returns the set of all card subtypes in this card list.

        Returns:
          The unique `list` of all card subtypes within the card list.
        '''
        return cast(list[str], self.collect_unique('subtypes'))

    def supertypes(self) -> list[str]:
        '''
        Returns the set of all card supertypes in this card list.

        Returns:
          The unique `list` of all card supertypes within the card list.
        '''
        return cast(list[str], self.collect_unique('supertypes'))

    def tags(self) -> list[str]:
        '''
        Returns the set of all user tags in this card list.

        Returns:
          The unique `list` of all user tags in the list.
        '''
        return cast(list[str], self.collect_unique('tags'))

    def talent_types(self) -> list[str]:
        '''
        Returns the set of all talent types in this card list.

        Returns:
          The unique `list` of all talent types within the card list.
        '''
        return cast(list[str], self.collect_unique('talent_type'))

    def to_dataframe(self) -> DataFrame:
        '''
        Converts the list of cards into a [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

        Returns:
          A pandas `DataFrame` object representing the list of cards.
        '''
        return DataFrame(copy.deepcopy(self.data))

    def to_flat_dataframe(self, fields: list[str]) -> DataFrame:
        '''
        Converts the list of cards into a [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

        The difference between this method and `to_dataframe()` is that the
        specified fields of type `list[str]` will be "exploded" into multiple
        entries per list element.

        Args:
          fields: A list of `Card` fields to invoke `DataFrame.explode()` on.

        Returns:
          A pandas `DataFrame` object representing the list of cards.
        '''
        result = self.to_dataframe()
        for field in fields:
            result = result.explode(field)
        result = result.replace([], None)
        return result

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

    def token_keywords(self) -> list[str]:
        '''
        Returns the set of all token keywords in this card list.

        Returns:
          The unique `list` of all token keywords within the card list.
        '''
        return cast(list[str], self.collect_unique('token_keywords'))

    def tokens(self) -> CardList:
        '''
        Returns the set of all token cards in this card list.

        Returns:
          The set of token cards in the list.
        '''
        return CardList(card for card in self.data if card.is_token())

    def total_cost(self) -> int:
        '''
        Computes the total card cost within this card list.

        Warning:
          Cards with variable or no cost are ignored.

        Returns:
          The total cost of all cards in the list.
        '''
        return cast(int, self.statistic('cost', 'total'))

    def total_defense(self) -> int:
        '''
        Computes the total card defense within this card list.

        Warning:
          Cards with variable or no defense are ignored.

        Returns:
          The total defense of all cards in the list.
        '''
        return cast(int, self.statistic('defense', 'total'))

    def total_intellect(self) -> int:
        '''
        Computes the total card intellect within this card list.

        Warning:
          Cards with variable or no intellect are ignored.

        Returns:
          The total intellect of all cards in the list.
        '''
        return cast(int, self.statistic('intellect', 'total'))

    def total_life(self) -> int:
        '''
        Computes the total card life value within this card list.

        Warning:
          Cards with variable or no life value are ignored.

        Returns:
          The total life value of all cards in the list.
        '''
        return cast(int, self.statistic('life', 'total'))

    def total_pitch(self) -> int:
        '''
        Computes the total card pitch value within this card list.

        Warning:
          Cards with variable or no pitch value are ignored.

        Returns:
          The total pitch value of all cards in the list.
        '''
        return cast(int, self.statistic('pitch', 'total'))

    def total_power(self) -> int:
        '''
        Computes the total attack power within this card list.

        Warning:
          Cards with variable or no attack power are ignored.

        Returns:
          The total attack power of all cards in the list.
        '''
        return cast(int, self.statistic('power', 'total'))

    def types(self) -> list[str]:
        '''
        Returns the set of all card types in this card list.

        Returns:
          The unique `list` of all card types in the list.
        '''
        return cast(list[str], self.collect_unique('types'))

    def type_keywords(self) -> list[str]:
        '''
        Returns the set of all type keywords in this card list.

        Returns:
          The unique `list` of all type keywords in the list.
        '''
        return cast(list[str], self.collect_unique('type_keywords'))

    def type_texts(self) -> list[str]:
        '''
        Returns the set of all type box texts in this card list.

        Returns:
          The unique `list` of all type box texts in the list.
        '''
        return cast(list[str], self.collect_unique('type_text'))

    def variations(self) -> list[str]:
        '''
        Returns the set of all card variations in this card list.

        Returns:
          The unique `list` of all card variations in the list.
        '''
        return cast(list[str], self.collect_unique('variations'))

    def weapons(self) -> CardList:
        '''
        Returns the set of all weapon cards in this card list.

        Returns:
          The set of all weapon cards in the list.
        '''
        return CardList(card for card in self.data if card.is_weapon())
