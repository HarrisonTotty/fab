'''
Contains tests for `CardSet` and `CardSetCollection` objects.
'''

import datetime

from fab import CardSet, CardSetCollection

from . import (
    C1,
    C2,
    C3,
    CS1,
    CSC1
)

def test_set_dict_rep():
    '''
    Tests the dictionary representation of `CardSet` objects.
    '''
    assert CS1['name'] == 'Monarch'
    assert set(CS1.keys()) == set([
        'editions',
        'identifier',
        'name',
        'release_date'
    ])
    assert dict(CS1) == {
        'editions': ['F', 'U'],
        'identifier': 'MON',
        'name': 'Monarch',
        'release_date': datetime.date(2021, 5, 7)
    }

def test_set_json_conversion():
    '''
    Tests the `CardSet.to_json()` and `CardSet.from_json()` methods.
    '''
    CS1_json = CS1.to_json()
    CS1_str = str(CS1)
    CS1_from_json = CardSet.from_json(CS1_json)
    assert CS1_json == CS1_str
    assert CS1_from_json == CS1

def test_set_values():
    '''
    Tests card set value via "dot" syntax.
    '''
    assert CS1.editions     == ['F', 'U']
    assert CS1.identifier   == 'MON'
    assert CS1.name         == 'Monarch'
    assert CS1.release_date == datetime.date(2021, 5, 7)

def test_set_collection_collections():
    '''
    Tests collection methods on `CardSetCollection` objects.
    '''
    assert set(CSC1.editions())      == set(['F', 'U', 'A', 'N'])
    assert set(CSC1.identifiers())   == set(['MON', 'WTR', 'UPR'])
    assert set(CSC1.names())         == set(['Monarch', 'Welcome to Rathe', 'Uprising'])
    assert set(CSC1.release_dates()) == set([
        datetime.date(2021, 5, 7), datetime.date(2019, 10, 11), datetime.date(2022, 6, 24)
    ])

def test_set_collection_get_release_date():
    '''
    Tests `CardSetCollection.get_release_date()`
    '''
    assert CSC1.get_release_date(C1) == datetime.date(2019, 10, 11)
    assert CSC1.get_release_date(C2) == datetime.date(2019, 10, 11)
    assert CSC1.get_release_date(C3) == datetime.date(2021, 5, 7)

def test_set_collection_json_conversion():
    '''
    Tests the `CardSetCollection.to_json()` and `CardSetCollection.from_json()`
    methods.
    '''
    CSC1_json = CSC1.to_json()
    CSC1_from_json = CardSetCollection.from_json(CSC1_json)
    assert CSC1_from_json == CSC1
