'''
Tests `Card` and `CardList` objects.
'''

from fab import Card, CardList

from . import (
    C1,
    C2,
    C3,
    CL1
)

def test_card_dict_rep():
    '''
    Tests the dictionary representation of card objects.
    '''
    assert C1['name'] == 'Crippling Crush'
    assert set(C1.keys()) == set([
        'body',
        'cost',
        'defense',
        'flavor_text',
        'full_name',
        'grants',
        'health',
        'identifiers',
        'image_urls',
        'intelligence',
        'keywords',
        'name',
        'pitch',
        'power',
        'rarities',
        'sets',
        'tags',
        'type_text',
        'types'
    ])
    assert dict(C1) == {
        'body': '**Bravo Specialization** *(You may only have Crippling Crush in your deck if your hero is Bravo.)*\n\n**Crush** - If Crippling Crush deals 4 or more damage to a hero, they discard 2 random cards.',
        'cost': 7,
        'defense': 3,
        'flavor_text': None,
        'full_name': 'Crippling Crush (1)',
        'grants': [],
        'health': None,
        'identifiers': ['1HP050', 'WTR043'],
        'image_urls': {'1HP050 - N': 'https://storage.googleapis.com/fabmaster/media/images/1HP050.width-450.png', 'WTR043 - A': 'https://storage.googleapis.com/fabmaster/media/images/WTR_43.width-450.png', 'WTR043 - U': 'https://storage.googleapis.com/fabmaster/media/images/U-WTR43.width-450.png'},
        'intelligence': None,
        'keywords': ['Bravo Specialization', 'Crush'],
        'name': 'Crippling Crush',
        'pitch': 1,
        'power': 11,
        'rarities': ['M', 'M'],
        'sets': ['1HP', 'WTR'],
        'tags': ['example-1'],
        'type_text': 'Guardian Action - Attack',
        'types': ['Guardian', 'Action', 'Attack']
    }

def test_card_json_conversion():
    '''
    Tests the JSON string representation of a card.
    '''
    C1_json = C1.to_json()
    C1_str = str(C1)
    C1_from_json = Card.from_json(C1_json)
    assert C1_json == C1_str
    assert C1_from_json == C1

def test_card_methods():
    '''
    Tests methods defined on card objects.
    '''
    assert C1.is_action()
    assert C1.is_attack()
    assert not C1.is_attack_reaction()
    assert not C1.is_aura()
    assert not C1.is_defense_reaction()
    assert not C1.is_equipment()
    assert not C1.is_hero()
    assert not C1.is_instant()
    assert not C1.is_item()
    assert not C1.is_reaction()
    assert not C1.is_token()
    assert not C1.is_weapon()
    assert C2.is_defense_reaction()
    assert C2.is_reaction()
    assert not C2.is_action()
    assert not C2.is_attack()
    assert not C2.is_attack_reaction()
    assert not C2.is_aura()
    assert not C2.is_equipment()
    assert not C2.is_hero()
    assert not C2.is_instant()
    assert not C2.is_item()
    assert not C2.is_token()
    assert not C2.is_weapon()
    assert C3.is_hero()
    assert not C3.is_action()
    assert not C3.is_attack()
    assert not C3.is_attack_reaction()
    assert not C3.is_aura()
    assert not C3.is_defense_reaction()
    assert not C3.is_equipment()
    assert not C3.is_instant()
    assert not C3.is_item()
    assert not C3.is_reaction()
    assert not C3.is_token()
    assert not C3.is_weapon()

def test_card_values():
    '''
    Tests card values via "dot" syntax.
    '''
    assert C1.cost    == 7
    assert C1.defense == 3
    assert C1.flavor_text is None
    assert C1.full_name == 'Crippling Crush (1)'
    assert C1.grants == []
    assert C1.health is None
    assert C1.identifiers == ['1HP050', 'WTR043']
    assert C1.intelligence is None
    assert C1.keywords == ['Bravo Specialization', 'Crush']
    assert C1.name == 'Crippling Crush'
    assert C1.pitch == 1
    assert C1.power == 11
    assert C1.rarities == ['M', 'M']
    assert C1.sets == ['1HP', 'WTR']
    assert C1.tags == ['example-1']
    assert C1.type_text == 'Guardian Action - Attack'
    assert C1.types == ['Guardian', 'Action', 'Attack']

def test_card_list_collections():
    '''
    Tests collection methods on card lists.
    '''
    assert set(CL1.costs()) == set([7, 0])
    assert set(CL1.defense_values()) == set([3])
    assert set(CL1.full_names()) == set(['Crippling Crush (1)', 'Flic Flak (2)', 'Chane'])
    assert set(CL1.grants()) == set(['Go again'])
    assert set(CL1.health_values()) == set([20])
    assert set(CL1.identifiers()) == set(['1HP050', 'WTR043', '1HP114', 'WTR093', 'HER037', 'CHN001', 'MON154'])
    assert set(CL1.intelligence_values()) == set([4])
    assert set(CL1.keywords()) == set(['Bravo Specialization', 'Crush', 'Go again'])
    assert set(CL1.names()) == set(['Crippling Crush', 'Flic Flak', 'Chane'])
    assert set(CL1.pitch_values()) == set([1, 2])
    assert set(CL1.power_values()) == set([11])
    assert set(CL1.rarities()) == set(['M', 'R', 'P', 'T'])
    assert set(CL1.sets()) == set(['1HP', 'WTR', 'HER', 'CHN', 'MON'])
    assert set(CL1.type_texts()) == set([
        'Guardian Action - Attack', 'Ninja - Defense Reaction', 'Shadow Runeblade Hero - Young'
    ])
    assert set(CL1.types()) == set([
        'Guardian', 'Action', 'Attack', 'Ninja', 'Defense Reaction', 'Shadow', 'Runeblade', 'Hero', 'Young'
    ])

def test_card_list_counts():
    '''
    Tests the `CardList.count()` method.
    '''
    assert CL1.counts() == {
        'Crippling Crush (1)': 1,
        'Flic Flak (2)': 1,
        'Chane': 1
    }

def test_card_list_filtering():
    '''
    Tests various invocations of the `CardList.filter()` method.
    '''
    # body
    assert set(CL1.filter(body='Bravo'))                        == set([C1])
    assert set(CL1.filter(body='Bravo', negate=True))              == set([C2, C3])
    # cost
    assert set(CL1.filter(cost=7))                              == set([C1])
    assert set(CL1.filter(cost=7, negate=True))                    == set([C2, C3])
    # defense
    assert set(CL1.filter(defense=3))                           == set([C1, C2])
    assert set(CL1.filter(defense=3, negate=True))                 == set([C3])
    # full name
    assert set(CL1.filter(full_name='Flic Flak (2)'))           == set([C2])
    assert set(CL1.filter(full_name='Flic Flak (2)', negate=True)) == set([C1, C3])
    # grants
    assert set(CL1.filter(grants='Go again'))                   == set([C3])
    assert set(CL1.filter(grants='Go again', negate=True))         == set([C1, C2])
    # health
    assert set(CL1.filter(health=20))                           == set([C3])
    assert set(CL1.filter(health=20, negate=True))                 == set([C1, C2])
    # intelligence
    assert set(CL1.filter(intelligence=4))                      == set([C3])
    assert set(CL1.filter(intelligence=4, negate=True))            == set([C1, C2])
    # keywords
    assert set(CL1.filter(keywords='Crush'))                    == set([C1])
    assert set(CL1.filter(keywords='Crush', negate=True))          == set([C2, C3])
    # name
    assert set(CL1.filter(name='Chane'))                        == set([C3])
    assert set(CL1.filter(name='Chane', negate=True))              == set([C1, C2])
    # pitch
    assert set(CL1.filter(pitch=(1,2)))                         == set([C1, C2])
    assert set(CL1.filter(pitch=(1,2), negate=True))               == set([C3])
    # power
    assert set(CL1.filter(power=11))                            == set([C1])
    assert set(CL1.filter(power=11, negate=True))                  == set([C2, C3])
    # sets
    assert set(CL1.filter(sets='MON'))                          == set([C3])
    assert set(CL1.filter(sets='MON', negate=True))                == set([C1, C2])
    # tags
    assert set(CL1.filter(tags='example-1'))                    == set([C1])
    assert set(CL1.filter(tags='example-1', negate=True))          == set([C2, C3])
    # type text
    assert set(CL1.filter(type_text='Hero'))                    == set([C3])
    assert set(CL1.filter(type_text='Hero', negate=True))          == set([C1, C2])
    # types
    assert set(CL1.filter(types='Attack'))                      == set([C1])
    assert set(CL1.filter(types='Attack', negate=True))            == set([C2, C3])

def test_card_list_iter():
    '''
    Tests the ability to iterate over card lists.
    '''
    assert len(CL1) == 3
    assert CL1[0] == C1
    for i, card in enumerate(CL1):
        assert card == [C1, C2, C3][i]

def test_card_list_json_conversion():
    '''
    Tests the JSON string conversion for `CardList` objects.
    '''
    CL_json = CL1.to_json()
    CL_from_json = CardList.from_json(CL_json)
    assert CL_from_json == CL1

def test_card_list_methods():
    '''
    Tests common `list` methods on cards.
    '''
    CL_append = CardList([C1, C2])
    CL_append.append(C3)
    assert CL_append == CardList([C1, C2, C3])
    CL_extend = CardList([C1])
    CL_extend.extend(CardList([C2, C3]))
    assert CL_extend == CardList([C1, C2, C3])
    CL_pop = CardList([C1, C2, C3])
    C3_popped = CL_pop.pop()
    assert C3_popped == C3
    assert CL_pop == CardList([C1, C2])

def test_card_list_sorting():
    '''
    Tests the `CardList.sort()` method.
    '''
    assert CL1.sort() == CardList([C3, C1, C2])
    assert CL1.sort(key = 'cost', reverse = True) == CardList([C1, C2, C3])
    assert CL1.sort(key = 'sets') == CardList([C1, C2, C3])
    assert CL1.sort(key = 'types') == CardList([C2, C1, C3])
    assert CL1.sort(key = 'rarities') == CardList([C2, C3, C1])

def test_card_list_statistics():
    '''
    Tests various card list statistics methods.
    '''
    assert CL1.max_cost()            == 7
    assert CL1.max_defense()         == 3
    assert CL1.max_health()          == 20
    assert CL1.max_intelligence()    == 4
    assert CL1.max_pitch()           == 2
    assert CL1.max_power()           == 11
    assert CL1.mean_cost()           == 3.5
    assert CL1.mean_defense()        == 3.0
    assert CL1.mean_health()         == 20.0
    assert CL1.mean_intelligence()   == 4.0
    assert CL1.mean_pitch()          == 1.5
    assert CL1.mean_power()          == 11.0
    assert CL1.median_cost()         == 3.5
    assert CL1.median_defense()      == 3.0
    assert CL1.median_health()       == 20.0
    assert CL1.median_intelligence() == 4.0
    assert CL1.median_pitch()        == 1.5
    assert CL1.median_power()        == 11.0
    assert CL1.min_cost()            == 0
    assert CL1.min_defense()         == 3
    assert CL1.min_health()          == 20
    assert CL1.min_intelligence()    == 4
    assert CL1.min_pitch()           == 1
    assert CL1.min_power()           == 11
    assert CL1.stdev_cost()          == 4.95
    assert CL1.stdev_defense()       == 0.0
    assert CL1.stdev_health()        == 0.0
    assert CL1.stdev_intelligence()  == 0.0
    assert CL1.stdev_pitch()         == 0.71
    assert CL1.stdev_power()         == 0.0
    assert CL1.total_cost()          == 7
    assert CL1.total_defense()       == 6
    assert CL1.total_health()        == 20
    assert CL1.total_intelligence()  == 4
    assert CL1.total_pitch()         == 3
    assert CL1.total_power()         == 11
    assert CL1.pitch_cost_difference()    == -4
    assert CL1.power_defense_difference() == 5
    assert CL1.statistics()['stdev_cost'] == 4.95
