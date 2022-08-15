'''
Contains useful meta information in the form of constants.

The value at the start of each docstring refers to the appropriate section of
the Comprehensive Rules document (if applicable).

The constants provided in this submodule are particularly useful when filtering
lists of cards, like so:

```python
# Returns all weapon cards in the list.
result = some_list.filter(types=meta.WEAPON_SUBTYPES)
```
'''

ABILITY_KEYWORDS = [
    'Arcane Barrier',
    'Attack',
    'Battleworn',
    'Blade Break',
    'Blood Debt',
    'Boost',
    'Dominate',
    'Essence',
    'Fusion',
    'Go again',
    'Heave',
    'Legendary',
    'Phantasm',
    'Quell',
    'Specialization',
    'Spectra',
    'Spellvoid',
    'Temper',
    'Ward'
]
'''
(8.3) Contains the set of all ability keywords.
'''

ALLY_SUBTYPES = [
    'Demon',
    'Dragon'
]
'''
Contains subtypes associated with ally cards.
'''

ART_TYPES = {
    'S': 'Standard',
    'AT': 'TODO: What is this?',
    'DS': 'Double Sided',
    'AA': 'Alternate Art',
    'EA': 'Extended Art',
    'FA': 'Full Art'
}
'''
Contains a mapping of card art types to their full name, in order by rarity.
'''

CARD_TYPES = [
    'Action',
    'Attack Reaction',
    'Defense Reaction',
    'Equipment',
    'Hero',
    'Instant',
    'Mentor',
    'Resource',
    'Token',
    'Weapon'
]
'''
(2.13.5) Contains the primary card types that may be present in the type box of a card.
'''

CLASS_SUPERTYPES = [
    'Adjudicator',
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
(2.10.6a) Contains card supertypes associated with the various hero classes.
'''

EDITIONS = {
    'A': 'Alpha',
    'F': 'First',
    'N': 'None',
    'U': 'Unlimited'
}
'''
Contains a mapping of card set edition codes to their full name.
'''

EFFECT_KEYWORDS = [
    'Add',
    'Banish',
    'Charge',
    'Create',
    'Deal',
    'Destroy',
    'Discard',
    'Distribute',
    'Draw',
    'Freeze',
    'Gain',
    'Ignore',
    'Intimidate',
    'Look',
    'Lose',
    'Negate',
    'Opt',
    'Pay',
    'Prevent',
    'Put',
    'Reload',
    'Remove',
    'Repeat',
    'Reroll',
    'Return',
    'Reveal',
    'Roll',
    'Search',
    'Shuffle',
    'Transform',
    'Turn',
    'Unfreeze'
]
'''
(8.5) Contains the set of all effect keywords, with the exception of continuous
effect keywords and "Name".

This also adds "Prevent" as a keyword.
'''

EQUIPMENT_SUBTYPES = [
    'Arms',
    'Chest',
    'Head',
    'Legs',
    'Off-Hand'
]
'''
Contains types associated with equipment slots, such as `Head`.
'''

FOILINGS = {
    'S': 'Standard',
    'R': 'Rainbow Foil',
    'C': 'Cold Foil',
    'P': 'Promotion Foiling', # TODO: This doesn't seem to be a thing, but upstream has it.
    'G': 'Gold Cold Foil',
}
'''
Contains a mapping of card foiling codes to their full names, in order by
rarity.
'''

FUNCTIONAL_SUBTYPES = [
    '1H',
    '2H',
    'Affliction',
    'Ally',
    'Arrow',
    'Attack',
    'Aura',
    'Invocation',
    'Item',
    'Landmark',
    'Trap'
]
'''
(2.9.6a) Contains the collection of all functional card subtypes.
'''

GAME_FORMATS = {
    'B': 'Blitz',
    'C': 'Commoner',
    'CC': 'Classic Constructed',
    'D': 'Draft',
    'UPF': 'Ultimate Pit Fight'
}
'''
Contains a mapping of game format codes to their full name.
'''

HERO_SUBTYPES = [
    'Young'
]
'''
Contains subtypes associated with hero cards.
'''

ICON_CODES = {
    '{d}': 'Defense',
    '{h}': 'Life',
    '{i}': 'Intellect',
    '{p}': 'Attack Power',
    '{r}': 'Resource Point',
}
'''
Contains a mapping of card body icon codes to their name.
'''

ICON_CODE_IMAGE_URLS = {
    '{d}': 'https://fabdb.net/img/defense.png',
    '{h}': 'https://fabdb.net/img/life.png',
    '{i}': 'https://fabdb.net/img/intellect.png',
    '{p}': 'https://fabdb.net/img/attack.png',
    '{r}': 'https://fabdb.net/img/resource.png',
}
'''
Contains a mapping of card body icon codes to their image URLs.
'''

LABEL_KEYWORDS = [
    'Channel',
    'Combo',
    'Crush',
    'Material',
    'Reprise',
    'Rupture'
]
'''
(8.4) Contains the set of all label keywords.
'''

RARITIES = {
    'T': 'Token',
    'C': 'Common',
    'R': 'Rare',
    'S': 'Super Rare',
    'M': 'Majestic',
    'V': 'Marvel',
    'L': 'Legendary',
    'P': 'Promotion',
    'F': 'Fabled'
}
'''
Contains a mapping of card rarity codes to their full name, in order of rarity.
'''

TALENT_SUPERTYPES = [
    'Draconic',
    'Earth',
    'Elemental',
    'Ice',
    'Light',
    'Lightning',
    'Shadow'
]
'''
(2.10.6b) Contains the card supertypes associated with talents.
'''

TOKEN_KEYWORDS = [
    'Aether Ashwing',
    'Ash',
    'Blasmophet, the Soul Harvester',
    'Copper',
    'Embodiment of Earth',
    'Embodiment of Lightning',
    'Frostbite',
    'Quicken',
    'Runechant',
    'Seismic Surge',
    'Silver',
    'Soul Shackle',
    'Spectral Shield',
    'Ursur, the Soul Reaper',
    'Zen State'
]
'''
Contains the set of all token keywords.
'''

WEAPON_SUBTYPES = [
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

# ----- Composite -----

KEYWORDS = ABILITY_KEYWORDS + EFFECT_KEYWORDS + LABEL_KEYWORDS + TOKEN_KEYWORDS
'''
(8.0) Contains the collection of all card keywords, with the exception of card type.
'''

NONFUNCTIONAL_SUBTYPES = ALLY_SUBTYPES + EQUIPMENT_SUBTYPES + HERO_SUBTYPES + WEAPON_SUBTYPES + ['Ash', 'Gem']
'''
(2.9.6b) Contains the collection of all non-functional subtypes.
'''

SUBTYPES = FUNCTIONAL_SUBTYPES + NONFUNCTIONAL_SUBTYPES
'''
(2.9) Contains the collection of all card subtypes.
'''

SUPERTYPES = CLASS_SUPERTYPES + TALENT_SUPERTYPES
'''
(2.10) Contains the collection of all card supertypes that may be found within
the card's `type_text`.
'''

TYPE_KEYWORDS = CARD_TYPES + FUNCTIONAL_SUBTYPES + SUPERTYPES + ['Effect']
'''
(8.1/8.2) Contains the list of type and subtype keywords that may be found within
the card's `body`.
'''
