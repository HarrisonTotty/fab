'''
Contains tests for `CardSet` objects.
'''

import datetime

from fab import CardSet

from . import (
    CS1,
    url_filler
)

def test_dict_rep():
    '''
    Tests the dictionary representation of `CardSet` objects.
    '''
    assert CS1['name'] == 'Monarch'
    assert set(CS1.keys()) == {
        'dates',
        'editions',
        'identifier',
        'id_range',
        'name',
        'urls'
    }
    assert dict(CS1) == {
        'dates': {'F': (datetime.date(2021, 5, 7), datetime.date(2021, 5, 7)), 'U': (datetime.date(2021, 6, 4), None)},
        'editions': ['F', 'U'],
        'identifier': 'MON',
        'id_range': ('MON000', 'MON306'),
        'name': 'Monarch',
        'urls': {'F': url_filler, 'U': url_filler}
    }

def test_json_conversion():
    '''
    Tests the `CardSet.to_json()` and `CardSet.from_json()` methods.
    '''
    CS1_json = CS1.to_json()
    CS1_from_json = CardSet.from_json(CS1_json)
    assert CS1_from_json == CS1

def test_set_values():
    '''
    Tests card set value via "dot" syntax.
    '''
    assert CS1.dates == {'F': (datetime.date(2021, 5, 7), datetime.date(2021, 5, 7)), 'U': (datetime.date(2021, 6, 4), None)}
    assert CS1.editions == ['F', 'U']
    assert CS1.identifier == 'MON'
    assert CS1.id_range == ('MON000', 'MON306')
    assert CS1.name == 'Monarch'
    assert CS1.urls == {'F': url_filler, 'U': url_filler}
