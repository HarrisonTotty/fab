'''
Contains methods associated with testing card inventories.
'''

# from fab import CardInventory, InventoryItem

# from . import (
#     INV1,
#     INVI1,
#     INVI2,
#     INVI3
# )

# def test_inventory_item_dict_rep():
#     '''
#     Tests the dictionary representation of `InventoryItem` objects.
#     '''
#     assert INVI1['identifier'] == 'WTR043'
#     assert set(INVI1.keys()) == set([
#         'edition',
#         'foiling',
#         'identifier',
#         'rarity'
#     ])
#     assert dict(INVI1) == {
#         'edition': 'U',
#         'foiling': 'S',
#         'identifier': 'WTR043',
#         'rarity': 'M'
#     }

# def test_inventory_item_json_conversion():
#     '''
#     Tests the `InventoryItem.to_json()` and `InventoryItem.from_json()` methods.
#     '''
#     INVI1_json = INVI1.to_json()
#     INVI1_from_json = InventoryItem.from_json(INVI1_json)
#     assert INVI1_from_json == INVI1

# def test_inventory_item_values():
#     '''
#     Tests the inventory item values via "dot" syntax.
#     '''
#     assert INVI1.edition    == 'U'
#     assert INVI1.foiling    == 'S'
#     assert INVI1.identifier == 'WTR043'
#     assert INVI1.rarity     == 'M'

# def test_inventory_collections():
#     '''
#     Tests the collection methods on `CardInventory` objects.
#     '''
#     assert set(INV1.editions())    == {'U'}
#     assert set(INV1.foilings())    == {'R', 'S'}
#     assert set(INV1.identifiers()) == {'WTR043', 'WTR093', 'CHN001'}
#     assert set(INV1.rarities())    == {'M', 'R'}

# def test_inventory_counts():
#     '''
#     Tests the counting methods on `CardInventory` objects.
#     '''
#     assert INV1.count()             == 3
#     assert INV1.edition_counts()    == {'U': 3}
#     assert INV1.foiling_counts()    == {'R': 1, 'S': 2}
#     assert INV1.identifier_counts() == {'WTR043': 1, 'WTR093': 1, 'CHN001': 1}
#     assert INV1.rarity_counts()     == {'M': 1, 'R': 2}

# def test_inventory_json_conversion():
#     '''
#     Tests converting `CardInventory` objects to/from JSON strings.
#     '''
#     INV1_json = INV1.to_json()
#     INV1_from_json = CardInventory.from_json(INV1_json)
#     assert INV1_from_json == INV1

# def test_inventory_lookups():
#     '''
#     Tests the `CardInventory.lookup()` method.
#     '''
#     assert set(INV1.lookup(set='WTR').keys()) == {INVI1, INVI2}

# def test_inventory_mutation():
#     '''
#     Tests various mutation methods on `CardInventory` objects.
#     '''
#     inv = CardInventory()
#     inv.add('WTR043', 'M', 'S')
#     assert inv.to_dict() == {
#         'U-WTR043-M-S': 1
#     }
#     inv.set('WTR043', 'M', 'S', count = 4)
#     assert inv.to_dict() == {
#         'U-WTR043-M-S': 4
#     }
#     inv.set('WTR043', 'M', 'S', count = 0)
#     assert inv.to_dict() == {
#         'U-WTR043-M-S': 0
#     }
