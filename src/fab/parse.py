'''
Contains methods associated with parsing raw card data.
'''

from __future__ import annotations

def compose_variation_str(art_type: str, edition: str, foiling: str, identifier: str, rarity: str) -> str:
    '''
    Composes the variation string from its components.
    '''
    return f'{identifier}-{edition}-{rarity}-{foiling}-{art_type}'

def decompose_variation_str(variation: str) -> dict[str, str]:
    '''
    Decomposes the variation string into a dictionary of its components.
    '''
    # {identifier}-{edition}-{rarity}-{foiling}-{art_type}
    chunks = variation.split('-')
    if len(chunks) != 5:
        raise Exception('invalid variation string')
    return {
        'art_type': chunks[4],
        'edition': chunks[1],
        'foiling': chunks[3],
        'identifier': chunks[0],
        'rarity': chunks[2],
        'set': ''.join(c for c in chunks[0] if not c.isdigit())
    }
