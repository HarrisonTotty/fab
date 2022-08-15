'''
Tests `CardList` objects.
'''

from fab import CardList

from . import (
    C1,
    C2,
    C3,
    CL1
)

def test_collections():
    '''
    Tests collection methods on card lists.
    '''
    assert CL1.ability_keywords() == ['Go again', 'Specialization']
    assert CL1.art_types() == ['S']
    assert CL1.card_types() == ['Action', 'Defense Reaction', 'Hero']
    assert CL1.class_types() == ['Guardian', 'Ninja', 'Runeblade']
    assert CL1.costs() == [0, 7]
    assert CL1.defense_values() == [3]
    assert CL1.editions() == ['A', 'F', 'N', 'U']
    assert CL1.effect_keywords() == ['Create', 'Deal', 'Discard', 'Gain']
    assert CL1.foilings() == ['S', 'R', 'C']
    assert CL1.full_names() == ['Chane', 'Crippling Crush (1)', 'Flic Flak (2)']
    assert CL1.grants_keywords() == ['Go again']
    assert CL1.intellect_values() == [4]
    assert CL1.keywords() == ['Action', 'Combo', 'Create', 'Crush', 'Deal', 'Discard', 'Gain', 'Go again', 'Soul Shackle', 'Specialization']
    assert CL1.label_keywords() == ['Combo', 'Crush']
    assert CL1.life_values() == [20]
    assert CL1.names() == ['Chane', 'Crippling Crush', 'Flic Flak']
    assert CL1.pitch_values() == [1, 2]
    assert CL1.power_values() == [11]
    assert CL1.rarities() == ['T', 'R', 'M', 'P']
    assert CL1.sets() == ['1HP', 'CHN', 'HER', 'MON', 'WTR']
    assert CL1.subtypes() == ['Attack', 'Young']
    assert CL1.supertypes() == ['Guardian', 'Ninja', 'Runeblade', 'Shadow']
    assert CL1.talent_types() == ['Shadow']
    assert CL1.token_keywords() == ['Soul Shackle']
    assert CL1.types() == ['Action', 'Attack', 'Defense Reaction', 'Guardian', 'Hero', 'Ninja', 'Runeblade', 'Shadow', 'Young']
    assert CL1.type_keywords() == ['Action']
    assert CL1.type_texts() == ['Guardian Action - Attack', 'Ninja - Defense Reaction', 'Shadow Runeblade Hero - Young']

def test_counts():
    '''
    Tests the `CardList.count()` method.
    '''
    assert CL1.counts() == {
        'Crippling Crush (1)': 1,
        'Flic Flak (2)': 1,
        'Chane': 1
    }

def test_filtering():
    '''
    Tests various invocations of the `CardList.filter()` method.
    '''
    # String Fields
    assert CL1.filter(body='Bravo').data == [C1]
    assert CL1.filter(body='Bravo', negate=True).data == [C2, C3]
    # Value Fields
    assert CL1.filter(cost=7).data == [C1]
    assert CL1.filter(cost=7, negate=True).data == [C2, C3]
    # String List Fields
    assert CL1.filter(keywords='Crush').data == [C1]
    assert CL1.filter(keywords='Crush', negate=True).data == [C2, C3]

def test_iter():
    '''
    Tests the ability to iterate over card lists.
    '''
    assert len(CL1) == 3
    assert CL1[0] == C1
    for i, card in enumerate(CL1):
        assert card == [C1, C2, C3][i]

def test_json_conversion():
    '''
    Tests the JSON string conversion for `CardList` objects.
    '''
    CL_json = CL1.to_json()
    CL_from_json = CardList.from_json(CL_json)
    assert CL_from_json == CL1

def test_list_methods():
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

def test_sorting():
    '''
    Tests the `CardList.sort()` method.
    '''
    assert CL1.sort().data == [C3, C1, C2]
    assert CL1.sort(by='cost', reverse = True).data == [C1, C2, C3]
    assert CL1.sort(by='sets').data == [C1, C2, C3]
    assert CL1.sort(by='types').data == [C2, C1, C3]
    assert CL1.sort(by='rarities').data == [C2, C1, C3]

def test_statistics():
    '''
    Tests various card list statistics methods.
    '''
    assert CL1.max_cost()         == 7
    assert CL1.max_defense()      == 3
    assert CL1.max_intellect()    == 4
    assert CL1.max_life()         == 20
    assert CL1.max_pitch()        == 2
    assert CL1.max_power()        == 11
    assert CL1.mean_cost()        == 3.5
    assert CL1.mean_defense()     == 3.0
    assert CL1.mean_intellect()   == 4.0
    assert CL1.mean_life()        == 20.0
    assert CL1.mean_pitch()       == 1.5
    assert CL1.mean_power()       == 11.0
    assert CL1.median_cost()      == 3.5
    assert CL1.median_defense()   == 3.0
    assert CL1.median_intellect() == 4.0
    assert CL1.median_life()      == 20.0
    assert CL1.median_pitch()     == 1.5
    assert CL1.median_power()     == 11.0
    assert CL1.min_cost()         == 0
    assert CL1.min_defense()      == 3
    assert CL1.min_intellect()    == 4
    assert CL1.min_life()         == 20
    assert CL1.min_pitch()        == 1
    assert CL1.min_power()        == 11
    assert CL1.num_blue()         == 0
    assert CL1.num_red()          == 1
    assert CL1.num_yellow()       == 1
    assert CL1.stdev_cost()       == 4.95
    assert CL1.stdev_defense()    == 0.0
    assert CL1.stdev_intellect()  == 0.0
    assert CL1.stdev_life()       == 0.0
    assert CL1.stdev_pitch()      == 0.71
    assert CL1.stdev_power()      == 0.0
    assert CL1.total_cost()       == 7
    assert CL1.total_defense()    == 6
    assert CL1.total_intellect()  == 4
    assert CL1.total_life()       == 20
    assert CL1.total_pitch()      == 3
    assert CL1.total_power()      == 11
    assert CL1.pitch_cost_difference()    == -4
    assert CL1.power_defense_difference() == 5
    assert CL1.statistics()['stdev_cost'] == 4.95
