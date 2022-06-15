'''
Provides tests against `Deck` objects.
'''

from fab import CardList, Deck

from . import (
    C1,
    C2,
    C3,
    D1
)

def test_deck_rep():
    '''
    Tests the dictionary/list representation of `Deck` objects.
    '''
    assert D1[0]        == C1
    assert len(D1)      == 2
    assert D1.to_dict() == {
        'cards': [C1.to_dict(), C2.to_dict()],
        'format': 'Blitz',
        'hero': C3.to_dict(),
        'inventory': [],
        'name': 'Test',
        'tokens': []
    }

def test_deck_all_cards():
    '''
    Tests the `Deck.all_cards()` method.
    '''
    assert D1.all_cards() == CardList([C3, C1, C2])

def test_deck_is_valid():
    '''
    Tests the `Deck.is_valid()` method.
    '''
    assert D1.is_valid()[0] == False

def test_deck_json_conversion():
    '''
    Tests the `Deck.to_json()` and `Deck.from_json()` methods.
    '''
    D1_json = D1.to_json()
    D1_from_json = Deck.from_json(D1_json)
    assert D1_from_json == D1

def test_deck_to_deck_list():
    '''
    Tests the `Deck.to_deck_list()` method.
    '''
    assert D1.to_deck_list() == {
        'Chane': 1,
        'Crippling Crush (1)': 1,
        'Flic Flak (2)': 1
    }

def test_deck_valid_types():
    '''
    Tests the `Deck.valid_types()` method.
    '''
    assert set(D1.valid_types()) == set([
        'Shadow', 'Runeblade', 'Generic'
    ])
