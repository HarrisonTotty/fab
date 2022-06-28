'''
Contains useful meta information.
'''

BLITZ_DECK_PRISM_DECKLIST = {
    'Prism': 1,
    'Dream Weavers': 1,
    'Enigma Chimera (2)': 2,
    'Enigma Chimera (3)': 2,
    'Halo of Illumination': 1,
    'Heartened Cross Strap': 1,
    'Herald of Judgment (2)': 1,
    'Herald of Protection (1)': 2,
    'Herald of Protection (3)': 2,
    'Herald of Ravages (1)': 2,
    'Herald of Ravages (3)': 2,
    'Herald of Rebirth (1)': 2,
    'Herald of Rebirth (3)': 2,
    'Herald of Tenacity (1)': 2,
    'Herald of Tenacity (3)': 2,
    'Illuminate (1)': 2,
    'Illuminate (3)': 2,
    'Iris of Reality': 1,
    'Merciful Retribution (2)': 1,
    'Ode to Wrath (2)': 1,
    'Phantasmify (1)': 1,
    'Prismatic Shield (1)': 2,
    'Prismatic Shield (3)': 1,
    'Rising Solartide (2)': 2,
    'Seek Enlightenment (1)': 2,
    'Spears of Surreality (3)': 2,
    'Spell Fray Leggings': 1,
    'The Librarian': 1,
    'Wartune Herald (1)': 2,
    'Wartune Herald (3)': 2
}

DIVINE_TYPES: list[str] = ['Light', 'Shadow']
'''
Contains divine card types, currently only `Light` and `Shadow`.
'''

ELEMENTAL_TYPES: list[str] = [
    'Lightning',
    'Ice',
    'Earth'
    # 'Fire' # Technically doesn't exist, but likely to.
]
'''
Contains elemental card types, such as `Earth` or `Ice`.

Note:
  `Light` and `Shadow` are _not_ considered elemental types, see `DIVINE_TYPES`
  instead.
'''

EQUIPMENT_SLOT_TYPES: list[str] = [
    'Arms',
    'Chest',
    'Head',
    'Legs',
    'Off-Hand'
]
'''
Contains types associated with equipment slots, such as `Head`.
'''

CLASS_TYPES: list[str] = [
    'Bard',
    'Brute',
    'Guardian',
    'Illusionist',
    'Mechanologist',
    'Merchant',
    'Ninja',
    'Ranger',
    'Runeblade',
    'Shapeshifter',
    'Warrior',
    'Wizard'
]
'''
Contains card types associated with the various hero classes, such as `Ninja`.
'''

GAME_FORMATS: list[str] = [
    'Blitz',
    'Classic Constructed',
    'Commoner',
    'Ultimate Pit Fight'
]
'''
Contains the names of the various game formats, such as `Blitz`.
'''

WEAPON_TYPES: list[str] = [
    'Axe',
    'Bow',
    'Claw',
    'Club',
    'Dagger',
    'Flail',
    'Gun',
    'Hammer',
    'Orb',
    'Pistol',
    'Scepter',
    'Scythe',
    'Staff',
    'Sword'
]
'''
Contains card types associated with the subtypes of weapons, such as `Sword`.
'''
