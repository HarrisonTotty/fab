'''
Module Unit Tests
'''

import datetime
import fab

def test_module_name():
    '''
    Tests the name of the module.
    '''
    assert fab.__name__ == 'fab'

# ----- Example Cards -----

C1 = fab.Card(
    ability_keywords = ['Specialization'],
    art_types        = ['S'],
    body             = '**Bravo Specialization** *(You may only have Crippling Crush in your deck if your hero is Bravo.)*\n\n**Crush** - If Crippling Crush deals 4 or more damage to a hero, they discard 2 random cards.',
    card_type        = 'Action',
    class_type       = 'Guardian',
    color            = 'Red',
    cost             = 7,
    dates            = {},
    defense          = 3,
    editions         = ['A', 'N', 'U'],
    effect_keywords  = ['Deal', 'Discard'],
    flavor_text      = None,
    foilings         = ['S', 'R'],
    full_name        = 'Crippling Crush (1)',
    grants_keywords  = [],
    identifiers      = ['1HP050', 'WTR043'],
    image_urls       = {},
    intellect        = None,
    keywords         = ['Crush', 'Deal', 'Discard', 'Specialization'],
    label_keywords   = ['Crush'],
    legality         = {'B': True, 'C': True, 'CC': True},
    life             = None,
    name             = 'Crippling Crush',
    pitch            = 1,
    power            = 11,
    rarities         = ['M'],
    sets             = ['1HP', 'WTR'],
    subtypes         = ['Attack'],
    supertypes       = ['Guardian'],
    talent_type      = None,
    token_keywords   = [],
    types            = ['Action', 'Attack', 'Guardian'],
    type_keywords    = [],
    type_text        = 'Guardian Action - Attack',
    variations       = ['1HP050-N-M-S-S', 'WTR043-A-M-R-S', 'WTR043-A-M-S-S', 'WTR043-U-M-R-S', 'WTR043-U-M-S-S'],
    notes            = None,
    tags             = ['example-1']
)

C2 = fab.Card(
    ability_keywords = [],
    art_types        = ['S'],
    body             = 'If the next card you defend with this turn is a card with **combo**, it gains +2{d}.',
    card_type        = 'Defense Reaction',
    class_type       = 'Ninja',
    color            = 'Yellow',
    cost             = 0,
    dates            = {},
    defense          = 3,
    editions         = ['A', 'N', 'U'],
    effect_keywords  = [],
    flavor_text      = 'Silver flashes under the pale moonlight, blades slicing through air as Ira twisted and turned, narrowly avoiding their ambush.',
    foilings         = ['S', 'R'],
    full_name        = 'Flic Flak (2)',
    grants_keywords  = [],
    identifiers      = ['1HP114', 'WTR093'],
    image_urls       = {},
    intellect        = None,
    keywords         = ['Combo'],
    label_keywords   = ['Combo'],
    legality         = {'B': True, 'C': True, 'CC': True},
    life             = None,
    name             = 'Flic Flak',
    pitch            = 2,
    power            = None,
    rarities         = ['R'],
    sets             = ['1HP', 'WTR'],
    subtypes         = [],
    supertypes       = ['Ninja'],
    talent_type      = None,
    token_keywords   = [],
    types            = ['Defense Reaction', 'Ninja'],
    type_keywords    = [],
    type_text        = 'Ninja - Defense Reaction',
    variations       = ['1HP114-N-R-S-S', 'WTR093-A-R-R-S', 'WTR093-A-R-S-S', 'WTR093-U-R-R-S', 'WTR093-U-R-S-S'],
    notes            = None,
    tags             = ['example-2'],
)

C3 = fab.Card(
    ability_keywords = ['Go again'],
    art_types        = ['S'],
    body             = '**Once per Turn Action** - Create a Soul Shackle token: Your next Runeblade or Shadow action this turn gains **go again. Go again** *(It\'s a Shadow Runeblade aura with "At the beginning of your action phase, banish the top card of your deck.")*',
    card_type        = 'Hero',
    class_type       = 'Runeblade',
    color            = None,
    cost             = None,
    dates            = {},
    defense          = None,
    editions         = ['F', 'N', 'U'],
    effect_keywords  = ['Create', 'Gain'],
    flavor_text      = None,
    foilings         = ['S', 'R', 'C'],
    full_name        = 'Chane',
    grants_keywords  = ['Go again'],
    identifiers      = ['HER037', 'CHN001', 'MON154'],
    image_urls       = {},
    intellect        = 4,
    keywords         = ['Action', 'Create', 'Gain', 'Go again', 'Soul Shackle'],
    label_keywords   = [],
    legality         = {'B': True, 'C': True, 'CC': True},
    life             = 20,
    name             = 'Chane',
    pitch            = None,
    power            = None,
    rarities         = ['T', 'R', 'P'],
    sets             = ['HER', 'CHN', 'MON'],
    subtypes         = ['Young'],
    supertypes       = ['Runeblade', 'Shadow'],
    talent_type      = 'Shadow',
    token_keywords   = ['Soul Shackle'],
    types            = ['Hero', 'Runeblade', 'Shadow', 'Young'],
    type_keywords    = ['Action'],
    type_text        = 'Shadow Runeblade Hero - Young',
    variations       = ['CHN001-N-R-R-S', 'HER037-N-P-C-S', 'MON154-F-T-S-S', 'MON154-U-T-S-S'],
    notes            = None,
    tags             = ['example-3']
)


# ----- Example Card Lists -----

CL1 = fab.CardList([C1, C2, C3])


# ----- Example Card Sets -----

url_filler = {
    'produce_page': 'FAKE',
    'collectors_center': 'FAKE',
    'card_gallery': 'FAKE'
}

CS1 = fab.CardSet(
    dates      = {'F': (datetime.date(2021, 5, 7), datetime.date(2021, 5, 7)), 'U': (datetime.date(2021, 6, 4), None)},
    editions   = ['F', 'U'],
    identifier = 'MON',
    id_range   = ('MON000', 'MON306'),
    name       = 'Monarch',
    urls       = {'F': url_filler, 'U': url_filler} # type: ignore
)

# CS2 = fab.CardSet(
#     dates      = {'A': (datetime.date(2019, 10, 11), datetime.date(2019, 10, 11)), 'U': (datetime.date(2020, 11, 6), datetime.date(2021, 12, 1))},
#     editions   = ['A', 'U'],
#     identifier = 'WTR',
#     id_range   = ('WTR000', 'WTR225'),
#     name       = 'Welcome to Rathe',
#     urls       = {'A': url_filler, 'U': url_filler} # type: ignore
# )

# CS3 = fab.CardSet(
#     dates      = {'N': (datetime.date(2022, 6, 24), None)},
#     editions   = ['N'],
#     identifier = 'UPR',
#     id_range   = ('UPR000', 'UPR225'),
#     name       = 'Uprising',
#     urls       = {'N': url_filler} # type: ignore
# )


# ----- Example Decks -----

D1 = fab.Deck(
    cards = fab.CardList([C1, C2]),
    hero  = C3,
    name  = 'Test'
)


# # ----- Example Card Inventory Items ------

# INVI1 = fab.InventoryItem(
#     identifier = 'WTR043',
#     rarity = 'M'
# )

# INVI2 = fab.InventoryItem(
#     identifier = 'WTR093',
#     rarity = 'R'
# )

# INVI3 = fab.InventoryItem(
#     identifier = 'CHN001',
#     rarity = 'R',
#     foiling = 'R'
# )


# # ----- Example Card Inventory Collections -----

# INV1 = fab.CardInventory({INVI1: 1, INVI2: 1, INVI3: 1})
