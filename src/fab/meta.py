'''
Contains useful meta information in the form of constants.
'''

DIVINE_TYPES: list[str] = ['Light', 'Shadow']
'''
Contains divine card types, currently only `Light` and `Shadow`.
'''

EDITIONS: dict[str, str] = {
    'A': 'Alpha',
    'F': 'First',
    'N': 'None',
    'U': 'Unlimited'
}
'''
Contains a mapping of card set edition codes to their full name.
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

FOILINGS: dict[str, str] = {
    'S': 'Standard',
    'R': 'Rainbow Foil',
    'C': 'Cold Foil',
    'G': 'Gold Cold Foil'
}
'''
Contains a mapping of card foiling codes to their full names.
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

GAME_FORMATS: dict[str, str] = {
    'B': 'Blitz',
    'C': 'Commoner',
    'CC': 'Classic Constructed',
    'UPF': 'Ultimate Pit Fight'
}
'''
Contains a mapping of game format codes to their full name.
'''

RARITIES: dict[str, str] = {
    'P': 'Promotion',
    'T': 'Token',
    'C': 'Common',
    'R': 'Rare',
    'S': 'Super Rare',
    'M': 'Majestic',
    'L': 'Legendary',
    'F': 'Fabled'
}
'''
Contains a mapping of card rarity codes to their full name.
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
