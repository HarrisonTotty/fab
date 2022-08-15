'''
Tests `Card` and `CardList` objects.
'''

from fab import Card

from . import (
    C1,
    C2,
    C3
)

def test_check_consistency():
    '''
    Checks the consistency of the three card objects and this method.
    '''
    assert C1.check_consistency() == (True, None)
    assert C2.check_consistency() == (True, None)
    assert C3.check_consistency() == (True, None)

def test_dict_rep():
    '''
    Tests the dictionary representation of card objects.
    '''
    assert C1['name'] == 'Crippling Crush'
    assert set(C1.keys()) == {
        'ability_keywords',
        'art_types',
        'body',
        'card_type',
        'class_type',
        'color',
        'cost',
        'dates',
        'defense',
        'editions',
        'effect_keywords',
        'flavor_text',
        'foilings',
        'full_name',
        'grants_keywords',
        'identifiers',
        'image_urls',
        'intellect',
        'keywords',
        'label_keywords',
        'legality',
        'life',
        'name',
        'pitch',
        'power',
        'rarities',
        'sets',
        'subtypes',
        'supertypes',
        'talent_type',
        'token_keywords',
        'types',
        'type_keywords',
        'type_text',
        'variations',
        'notes',
        'tags'
    }
    assert dict(C1) == {
        'ability_keywords': ['Specialization'],
        'art_types': ['S'],
        'body': '**Bravo Specialization** *(You may only have Crippling Crush in your deck if your hero is Bravo.)*\n\n**Crush** - If Crippling Crush deals 4 or more damage to a hero, they discard 2 random cards.',
        'card_type': 'Action',
        'class_type': 'Guardian',
        'color': 'Red',
        'cost': 7,
        'dates': {},
        'defense': 3,
        'editions': ['A', 'N', 'U'],
        'effect_keywords': ['Deal', 'Discard'],
        'flavor_text': None,
        'foilings': ['S', 'R'],
        'full_name': 'Crippling Crush (1)',
        'grants_keywords': [],
        'identifiers': ['1HP050', 'WTR043'],
        'image_urls': {},
        'intellect': None,
        'keywords': ['Crush', 'Deal', 'Discard', 'Specialization'],
        'legality': {'B': True, 'C': True, 'CC': True},
        'label_keywords': ['Crush'],
        'life': None,
        'name': 'Crippling Crush',
        'pitch': 1,
        'power': 11,
        'rarities': ['M'],
        'sets': ['1HP', 'WTR'],
        'subtypes': ['Attack'],
        'supertypes': ['Guardian'],
        'talent_type': None,
        'token_keywords': [],
        'types': ['Action', 'Attack', 'Guardian'],
        'type_keywords': [],
        'type_text': 'Guardian Action - Attack',
        'variations': ['1HP050-N-M-S-S', 'WTR043-A-M-R-S', 'WTR043-A-M-S-S', 'WTR043-U-M-R-S', 'WTR043-U-M-S-S'],
        'notes': None,
        'tags': ['example-1'],
    }

def test_json_conversion():
    '''
    Tests the JSON string representation of a card.
    '''
    C1_json = C1.to_json()
    C1_str = str(C1)
    C1_from_json = Card.from_json(C1_json)
    assert C1_json == C1_str
    assert C1_from_json == C1

def test_methods():
    '''
    Tests methods defined on card objects.
    '''
    assert C1.is_action()
    assert C1.is_attack()
    assert C1.is_red()
    assert not C1.is_attack_reaction()
    assert not C1.is_aura()
    assert not C1.is_blue()
    assert not C1.is_defense_reaction()
    assert not C1.is_equipment()
    assert not C1.is_generic()
    assert not C1.is_hero()
    assert not C1.is_instant()
    assert not C1.is_item()
    assert not C1.is_reaction()
    assert not C1.is_token()
    assert not C1.is_weapon()
    assert not C1.is_yellow()
    assert C2.is_defense_reaction()
    assert C2.is_reaction()
    assert C2.is_yellow()
    assert not C2.is_action()
    assert not C2.is_attack()
    assert not C2.is_attack_reaction()
    assert not C2.is_aura()
    assert not C2.is_blue()
    assert not C2.is_equipment()
    assert not C2.is_generic()
    assert not C2.is_hero()
    assert not C2.is_instant()
    assert not C2.is_item()
    assert not C2.is_red()
    assert not C2.is_token()
    assert not C2.is_weapon()
    assert C3.is_hero()
    assert not C3.is_action()
    assert not C3.is_attack()
    assert not C3.is_attack_reaction()
    assert not C3.is_aura()
    assert not C3.is_blue()
    assert not C3.is_defense_reaction()
    assert not C3.is_equipment()
    assert not C3.is_generic()
    assert not C3.is_instant()
    assert not C3.is_item()
    assert not C3.is_reaction()
    assert not C3.is_red()
    assert not C3.is_token()
    assert not C3.is_weapon()
    assert not C3.is_yellow()

def test_values():
    '''
    Tests card values via "dot" syntax.
    '''
    assert C1.ability_keywords == ['Specialization']
    assert C1.art_types == ['S']
    assert C1.card_type == 'Action'
    assert C1.class_type == 'Guardian'
    assert C1.color == 'Red'
    assert C1.cost == 7
    assert C1.defense == 3
    assert C1.editions == ['A', 'N', 'U']
    assert C1.effect_keywords == ['Deal', 'Discard']
    assert C1.flavor_text is None
    assert C1.foilings == ['S', 'R']
    assert C1.full_name == 'Crippling Crush (1)'
    assert C1.grants_keywords == []
    assert C1.identifiers == ['1HP050', 'WTR043']
    assert C1.intellect is None
    assert C1.keywords == ['Crush', 'Deal', 'Discard', 'Specialization']
    assert C1.label_keywords == ['Crush']
    assert C1.legality == {'B': True, 'C': True, 'CC': True}
    assert C1.life is None
    assert C1.name == 'Crippling Crush'
    assert C1.notes is None
    assert C1.pitch == 1
    assert C1.power == 11
    assert C1.rarities == ['M']
    assert C1.sets == ['1HP', 'WTR']
    assert C1.subtypes == ['Attack']
    assert C1.supertypes == ['Guardian']
    assert C1.talent_type is None
    assert C1.token_keywords == []
    assert C1.tags == ['example-1']
    assert C1.type_keywords == []
    assert C1.type_text == 'Guardian Action - Attack'
    assert C1.types == ['Action', 'Attack', 'Guardian']

def test_tcgplayer_integration():
    '''
    Tests methods on cards and card lists associated with TCG Player.
    '''
    assert C1.tcgplayer_url() == 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q=Crippling Crush'
    assert C2.tcgplayer_url() == 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q=Flic Flak'
    assert C3.tcgplayer_url() == 'https://www.tcgplayer.com/search/flesh-and-blood-tcg/product?q=Chane'
