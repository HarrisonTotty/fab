'''
Contains the definition of a card catalog.
'''

from __future__ import annotations

import copy
import csv
import datetime
import gzip
import io
import json
import os
from numpy import indices
import requests
import tempfile
import zipfile

from typing import Any, cast, Iterable, Optional
from unidecode import unidecode

from .card import Card, STRING_FIELDS, STRING_LIST_FIELDS, VALUE_FIELDS
from .card_list import CardList
from .card_set import CardSet
from .meta import (
    ABILITY_KEYWORDS,
    ART_TYPES,
    CARD_TYPES,
    CLASS_SUPERTYPES,
    EDITIONS,
    EFFECT_KEYWORDS,
    FOILINGS,
    FUNCTIONAL_SUBTYPES,
    LABEL_KEYWORDS,
    RARITIES,
    SUBTYPES,
    SUPERTYPES,
    TALENT_SUPERTYPES,
    TOKEN_KEYWORDS,
    TYPE_KEYWORDS
)

DEFAULT_CATALOG: Optional[CardCatalog] = None
DEFAULT_BASE_URL: str = 'https://github.com/HarrisonTotty/fab/releases/download'
UPSTREAM_DATE_FORMAT: str = '%Y-%m-%d'
UPSTREAM_BASE_URL: str = 'https://github.com/flesh-cube/flesh-and-blood-cards/releases/download'

def _parse_full_name(name: str, pitchstr: str) -> str:
    '''
    A helper function for parsing out the full name of a card.
    '''
    decoded = unidecode(name).strip()
    stripped_pitch = pitchstr.strip()
    if stripped_pitch.isdigit():
        return f'{decoded} ({stripped_pitch})'
    else:
        return decoded

def _parse_legality(entry: dict[str, Any]) -> dict[str, bool]:
    '''
    A helper function for parsing out card legality from upstream data.
    '''
    res = {}
    try:
        blitz_legal = not entry['Blitz Legal'].lower() in ['no', 'false']
        blitz_ll = True if entry['Blitz Living Legend'] else False
        blitz_banned = True if entry['Blitz Banned'] else False
        cc_legal = not entry['CC Legal'].lower() in ['no', 'false']
        cc_ll = True if entry['CC Living Legend'] else False
        cc_banned = True if entry['CC Banned'] else False
        commoner_legal = not entry['Commoner Legal'].lower() in ['no', 'false']
        commoner_banned = True if entry['Commoner Banned'] else False
        res['B'] = blitz_legal and not blitz_ll and not blitz_banned
        res['CC'] = cc_legal and not cc_ll and not cc_banned
        res['C'] = commoner_legal and not commoner_banned
    except Exception as e:
        raise Exception(f'unable to parse card legality - {e}')
    return res

def _parse_image_urls(inputstr: str) -> list[str]:
    '''
    A helper function for parsing out the image URL list from upstream data.
    '''
    result = []
    try:
        if not inputstr:
            return result
        elif ',' in inputstr:
            for substrings in [x.split(' - ', 1) for x in unidecode(inputstr).split(',') if ' - ' in x]:
                url = substrings[0].strip()
                result.append(url)
        elif ' - ' in inputstr:
            url = unidecode(inputstr).split(' - ', 1)[0].strip()
            result.append(url)
    except Exception as e:
        raise Exception(f'unable to parse image URLs - {e}')
    return result

def _parse_keywords(
    abilities_and_effects_str: str,
    abilities_and_effects_keywords_str: str,
    body: str,
    card_keywords_str: str,
    granted_keywords_str: str
) -> dict[str, list[str]]:
    '''
    A helper function for parsing out card keywords.
    '''
    # First, let's set things up by converting the upstream data into some lists
    # stripped of whitespace.
    try:
        abilities_and_effects = [k.strip() for k in unidecode(abilities_and_effects_str).split(',')]
        abilities_and_effects_keywords = [k.strip() for k in unidecode(abilities_and_effects_keywords_str).split(',')]
        card_keywords = [k.strip() for k in unidecode(card_keywords_str).split(',')]
        granted_keywords = [k.strip() for k in unidecode(granted_keywords_str).split(',')]
    except Exception as e:
        raise Exception(f'unable to split keyword strings - {e}')
    # This will be the form of our result.
    res = {
        'ability_keywords': [],
        'effect_keywords': [],
        'grants_keywords': [],
        'keywords': [],
        'label_keywords': [],
        'token_keywords': [],
        'type_keywords': []
    }
    # Start by aggregating the non-grant fields and see if any of the keywords
    # defined in `meta` are contained in the aggregate. We'll save the results
    # to the `keywords` key and then further process afterwards.
    try:
        for k in abilities_and_effects + abilities_and_effects_keywords + card_keywords:
            no_digits = ''.join(c for c in k if not c.isdigit()).strip()
            # delete "turn" from the upstream keyword data because it gets
            # confused for the "Turn" effect keyword.
            no_digits = no_digits.replace('turn', '').replace('Turn', '')
            for other in sorted(ABILITY_KEYWORDS + EFFECT_KEYWORDS + LABEL_KEYWORDS + TYPE_KEYWORDS, key=len, reverse=True):
                if other == no_digits or other in no_digits.split():
                    if not other in res['keywords']:
                        res['keywords'].append(other)
    except Exception as e:
        raise Exception(f'unable to aggregate non-grant keyword fields - {e}')
    # Next, let's  do some additional work by parsing what keys we can directly
    # from the body of the card. We'll need to work with all alphanumeric text
    # that isn't part of the reminder text.
    if body:
        try:
            for paragraph in unidecode(body).split('\n\n'):
                clean = paragraph.replace('Turn', '').replace('turn', '').rsplit('*(', 1)[0]
                clean = ''.join(c for c in clean if c.isalnum() or c.isspace())
                for k in LABEL_KEYWORDS:
                    if k.lower() in clean.lower():
                        if not k in res['keywords']:
                            res['keywords'].append(k)
                for k in EFFECT_KEYWORDS:
                    if k.lower() in clean.lower():
                        if not k in res['keywords']:
                            res['keywords'].append(k)
                for k in TOKEN_KEYWORDS:
                    if k in clean:
                        if not k in res['keywords']:
                            res['keywords'].append(k)
        except Exception as e:
            raise Exception(f'unable to parse keywords from card body - {e}')
    # Now parse the grants keywords.
    try:
        for k in granted_keywords:
            no_digits = ''.join(c for c in k if not c.isdigit()).strip()
            if no_digits in ABILITY_KEYWORDS + LABEL_KEYWORDS:
                if not no_digits in res['keywords']:
                    res['keywords'].append(no_digits)
                res['grants_keywords'].append(no_digits)
    except Exception as e:
        raise Exception(f'unable to parse grants keywords - {e}')
    # Now let's go back through the `keywords` key and further split the
    # keywords into the appropriate list.
    res['keywords'] = sorted(res['keywords'])
    for k in res['keywords']:
        if k in ABILITY_KEYWORDS:
            res['ability_keywords'].append(k)
        elif k in EFFECT_KEYWORDS:
            res['effect_keywords'].append(k)
        elif k in LABEL_KEYWORDS:
            res['label_keywords'].append(k)
        elif k in TOKEN_KEYWORDS:
            res['token_keywords'].append(k)
        elif k in TYPE_KEYWORDS:
            res['type_keywords'].append(k)
        else:
            raise Exception(f'unexpected keyword "{k}"')
    return {k: sorted(v) for k, v in res.items()}

def _parse_markdown_text(inputstr: str) -> Optional[str]:
    '''
    A helper function to parse the body and flavor text of cards.
    '''
    stripped = inputstr.strip()
    if not stripped:
        return None
    else:
        return unidecode(stripped)

def _parse_set_edition_data(editions_str: str, irds_str: str, oopds_str: str, pp_str: str, cc_str: str, cg_str: str) -> dict[str, Any]:
    '''
    A helper function to parse all set data tied to edition information.
    '''
    try:
        editions = [e.strip() for e in editions_str.split(',')]
        irds = [d.strip() for d in irds_str.split(',')]
        oopds = [d.strip() for d in oopds_str.split(',')]
        pp = [s.strip() for s in pp_str.split(',')]
        cc = [s.strip() for s in cc_str.split(',')]
        cg = [s.strip() for s in cg_str.split(',')]
    except Exception as e:
        raise Exception(f'unable to split set edition strings - {e}')
    res = {
        'editions': editions,
        'dates': {},
        'urls': {}
    }
    for i, edition in enumerate(editions):
        date_strings: list[Optional[str]] = []
        try:
            if len(irds) > i:
                date_strings.append(
                    irds[i].split('T', 1)[0] if 'T' in irds[i] else None
                )
            else:
                date_strings.append(None)
            if len(oopds) > i:
                date_strings.append(
                    oopds[i].split('T', 1)[0] if 'T' in oopds[i] else None
                )
            else:
                date_strings.append(None)
        except Exception as e:
            raise Exception(f'unable to pre-parse date strings - {e}')
        try:
            dates = (
                datetime.datetime.strptime(date_strings[0], UPSTREAM_DATE_FORMAT).date() if not date_strings[0] is None else None,
                datetime.datetime.strptime(date_strings[1], UPSTREAM_DATE_FORMAT).date() if not date_strings[1] is None else None
            )
        except Exception as e:
            raise Exception(f'unable to parse date strings - {e}')
        try:
            if len(pp) > i:
                product_page = pp[i].strip() if pp[i] else None
                if product_page == 'null': product_page = None
            else:
                product_page = None
            if len(cc) > i:
                collectors_center = cc[i].strip() if cc[i] else None
                if collectors_center == 'null': collectors_center = None
            else:
                collectors_center = None
            if len(cg) > i:
                card_gallery = cg[i].strip() if cg[i] else None
                if card_gallery == 'null': card_gallery = None
            else:
                card_gallery = None
        except Exception as e:
            raise Exception(f'unable to parse set urls - {e}')
        res['dates'][edition] = dates
        res['urls'][edition] = {
            'product_page': product_page,
            'collectors_center': collectors_center,
            'card_gallery': card_gallery
        }
    return res

def _parse_set_start_end_id(startid_str: str, endid_str: str) -> tuple[Optional[str], Optional[str]]:
    '''
    A helper function to parse the start and end card identifiers for a set.
    '''
    startid = startid_str.strip() if startid_str else None
    endid = endid_str.strip() if endid_str else None
    return (startid, endid)

def _parse_types(inputstr: str) -> dict[str, Optional[list[str] | str]]:
    '''
    A helper function for parsing card type information.
    '''
    try:
        all_types = [t.strip() for t in unidecode(inputstr).split(',')]
        res = {
            'card_type': 'UNKNOWN',
            'class_type': None,
            'subtypes': sorted([t for t in all_types if t in SUBTYPES]),
            'supertypes': sorted([t for t in all_types if t in SUPERTYPES]),
            'types': sorted(all_types),
            'talent_type': None
        }
        for t in all_types:
            if t in CARD_TYPES:
                res['card_type'] = t
        # If we couldn't figure out the card type, assume it's a token.
        if res['card_type'] == 'UNKNOWN': res['card_type'] = 'Token'
        for t in res['supertypes']:
            if t in CLASS_SUPERTYPES:
                res['class_type'] = t
            elif t in TALENT_SUPERTYPES:
                res['talent_type'] = t
        return res
    except Exception as e:
        raise Exception(f'unable to parse card types - {e}')

def _parse_value(inputstr: str) -> int | str | None:
    '''
    A helper function for parsing stuff like card cost from upstream CSV data.
    '''
    if not inputstr or inputstr.lower() in ['none', 'null']:
        return None
    elif inputstr.isdigit():
        return int(inputstr)
    else:
        return inputstr

def _parse_variations(identifiers_str: str, rarities_str: str, variations_str: str) -> dict[str, list[str]]:
    '''
    A helper function for parsing card variations (like editions and foilings)
    from upstream data.
    '''
    # First, we need to clean up our identifiers and rarities. We'll be building
    # a map of `identifier -> edition -> rarity` so that we may build the
    # variations strings easier.
    try:
        identifiers: list[str] = [i.strip() for i in unidecode(identifiers_str).split(',')]
    except Exception as e:
        raise Exception(f'unable to parse card identifiers - {e}')
    try:
        rarities_map: dict[str, dict[str, list[str]]] = {}
        for i, rarity_chunk in enumerate(unidecode(rarities_str).split(',')):
            if not '-' in rarity_chunk:
                rarity = rarity_chunk.strip()
                if not rarity in RARITIES: continue
                if len(identifiers) >= i + 1:
                    if not identifiers[i] in rarities_map:
                        rarities_map[identifiers[i]] = {}
                    if not 'any' in rarities_map[identifiers[i]]:
                        rarities_map[identifiers[i]]['any'] = [rarity]
                    else:
                        rarities_map[identifiers[i]]['any'].append(rarity)
                else:
                    continue
            else:
                rpart_chunks = rarity_chunk.strip().split('-')
                if len(rpart_chunks) < 3: continue
                identifier = rpart_chunks[1].strip()
                edition = rpart_chunks[2].strip()
                if not edition in EDITIONS: continue
                rarities = [r.strip() for r in rpart_chunks[0].strip().split()]
                if not identifier in rarities_map:
                    rarities_map[identifier] = {}
                rarities_map[identifier][edition] = [r for r in rarities if r in RARITIES]
    except Exception as e:
        raise Exception(f'unable to parse and compute card rarities map - {e}')
    # This is needed because remember that the rarities string can contain `-`
    # characters.
    rarities: list[str] = []
    for edition in rarities_map.values():
        for rs in edition.values():
            rarities.extend(rs)
    # This is the format of our result dictionary.
    res = {
        'art_types': ['S'],
        'editions': [],
        'foilings': [],
        'identifiers': list(set(identifiers)),
        'rarities': list(set(rarities)),
        'variations': []
    }
    # If we aren't provided an explicit variations string, we'll have to assume
    # that all combinations are possible. We'll also assume that any unknown
    # edition is "Unlimited", and art types and foilings are "Standard".
    if not variations_str:
        try:
            variations = []
            for identifier, idata in rarities_map.items():
                for edition, rarity in idata.items():
                    if edition == 'any':
                        if not 'U' in res['editions']:
                            res['editions'].append('U')
                        variations.append(f'{identifier}-U-{rarity}-S-S')
                    else:
                        if not edition in res['editions']:
                            res['editions'].append(edition)
                        variations.append(f'{identifier}-{edition}-{rarity}-S-S')
            for v in variations:
                if not v in res['variations']:
                    res['variations'].append(v)
            res['art_types'].append('S')
            res['foilings'].append('S')
        except Exception as e:
            raise Exception(f'unable to compute fallback card variations - {e}')
    else:
        try:
            for raw_variation in unidecode(variations_str).split(','):
                chunks = raw_variation.strip().split('-')
                if len(chunks) < 3:
                    continue
                variations = []
                foilings = chunks[0].strip().split()
                identifier = chunks[1].strip()
                edition = chunks[2].strip()
                if not edition in EDITIONS: continue
                art_type = chunks[3].strip() if len(chunks) == 4 else 'S'
                if not art_type in ART_TYPES: continue
                for foiling in foilings:
                    if not foiling in FOILINGS: continue
                    for rarity in (rarities_map[identifier]['any'] if 'any' in rarities_map[identifier] else rarities_map[identifier][edition]):
                        variations.append(f'{identifier}-{edition}-{rarity}-{foiling}-{art_type}')
                    if not foiling in res['foilings']:
                        res['foilings'].append(foiling)
                if not edition in res['editions']:
                    res['editions'].append(edition)
                if not art_type in res['art_types']:
                    res['art_types'].append(art_type)
                for v in variations:
                    if not v in res['variations']:
                        res['variations'].append(v)
        except Exception as e:
            raise Exception(f'unable to parse card variations - {e}')
    # Before we return the data, let's sort it.
    try:
        return {
            'art_types': sorted(res['art_types'], key=lambda a: list(ART_TYPES.keys()).index(a)),
            'editions': sorted(res['editions']),
            'foilings': sorted(res['foilings'], key=lambda f: list(FOILINGS.keys()).index(f)),
            'identifiers': sorted(res['identifiers']),
            'rarities': sorted(res['rarities'], key=lambda r: list(RARITIES.keys()).index(r)),
            'variations': sorted(res['variations'])
        }
    except Exception as e:
        raise Exception(f'unable to sort card variation data - {e}')

class CardCatalog:
    '''
    Represents a card catalog of Flesh and Blood cards.

    This object is designed to contain a large volume of `Card` objects which
    have certain mappings computed at init-time. Other mappings are produced
    on-demand. Each mapping is a `dict` that correlates a certain possible card
    field value with one or more indices in the `data` field. In general, one
    does not need to access these fields (attributes) directly, but they are
    documented below nonetheless.

    Attributes:
      card_data: Contains a raw `list` of all available cards.
      card_full_name_mapping: Maps the full names of cards to their corresponding index in `card_data`.
      card_identifier_mapping: Maps the identifiers of cards to their corresponding index in `card_data`.
      card_mapping_cache: A cache of mappings between card fields and their corresponding indices in `card_data`.
      card_variation_mapping: Maps the variation codes of cards to their corresponding index in `card_data`.
      set_data: Contains a raw `list` of all available card sets.
      set_identifier_mapping: Maps the identifiers of card sets to their corresponding index in `set_data`.
      set_name_mapping: Maps the names of card sets to their corresponding index in `set_data`.
    '''
    card_data: list[Card]
    card_full_name_mapping: dict[str, int]
    card_identifier_mapping: dict[str, int]
    card_mapping_cache: dict[str, dict[Optional[int | str], list[int]]]
    card_variation_mapping: dict[str, int]
    set_data: list[CardSet]
    set_identifier_mapping: dict[str, int]
    set_name_mapping: dict[str, int]

    def __getitem__(self, key: int | slice | str) -> Card | CardList:
        '''
        Allows one to obtain cards via index notation.

        Args:
          key: The query provided to the catalog.

        Returns:
          A single card by position if `key` is an `int`, a list of cards if
          `key` is a `slice`, or a single card by identifier if `key` is an
          identifier string.
        '''
        if isinstance(key, int):
            return self.card_data[key]
        elif isinstance(key, slice):
            return CardList(self.card_data[key])
        elif isinstance(key, str):
            return self.lookup_card(identifier=key)
        else:
            raise ValueError('specified key is not an integer, slice, or identifier string')

    def __hash__(self) -> Any:
        '''
        Computes the hash representation of the catalog.

        Returns:
          The hash value of the catalog.
        '''
        return hash((self.card_data, self.set_data))

    def __init__(self, card_data: list[Card], set_data: list[CardSet]) -> None:
        '''
        Initializes a new card catalog from the specified card and set data.

        Args:
          card_data: The list of cards to build the catalog from.
          card_set_data: The list of card sets to build the catalog from.
        '''
        self.card_data = copy.deepcopy(card_data)
        self.set_data = copy.deepcopy(set_data)
        self.recompute_base_mapping()
        self.clean_mapping_cache()

    def __iter__(self) -> Iterable[Card]:
        '''
        Allows one to iterate over a catalog.
        '''
        yield from self.card_data

    def __len__(self) -> int:
        '''
        Returns the total number of cards managed by this catalog.

        Returns:
          The number of cards managed by the catalog.
        '''
        return len(self.card_data)

    def cards(self) -> CardList:
        '''
        Returns the list of all cards contained within the catalog.

        Returns:
          The list of all cards contained within the catalog.
        '''
        return CardList(self.card_data)

    def clean_mapping_cache(self) -> None:
        '''
        Cleans the mapping caches for all catalog mappings except for card
        mappings by full name and identifier, and set mappings by name and
        identifier.
        '''
        self.card_mapping_cache = {}

    @staticmethod
    def from_dict(data: dict[str, list[dict]]) -> CardCatalog:
        '''
        Creates a card catalog from its dictionary representation.

        Args:
          data: The dictionary representation of the card catalog to convert from.

        Returns:
          A new card catalog from the specified data.
        '''
        return CardCatalog(
            card_data = [Card.from_dict(d) for d in data['card_data']],
            set_data = [CardSet.from_dict(d) for d in data['set_data']]
        )

    @staticmethod
    def from_json(jsonstr: str) -> CardCatalog:
        '''
        Creates a card catalog from its JSON string representation.

        Args:
          jsonstr: The JSON string representation of the card catalog to convert from.

        Returns:
          A new card catalog from the specified data.
        '''
        return CardCatalog.from_dict(json.loads(jsonstr))

    @staticmethod
    def import_upstream(version: str = 'v2.8.1', set_default: bool = False) -> CardCatalog:
        '''
        Imports card data from the upstream [data
        repository](https://github.com/flesh-cube/flesh-and-blood-cards).

        Args:
          version: The release version of the upstream repository to download.
          set_default: Whether to set the loaded catalog as the global default catalog.

        Returns:
          A new card catalog parsed from the upstream repository data.
        '''
        # 1. Pull the .zip file from the web.
        url = f'{UPSTREAM_BASE_URL}/{version}/csvs.zip'
        with tempfile.NamedTemporaryFile(
                prefix = f'fab-upstream-{version}-',
                suffix = '.zip',
                delete = False
        ) as f:
            f.write(requests.get(url).content)
            file_name = f.name
        # 2. Open the internal CSV files and pre-parse them via `DictReader`.
        with zipfile.ZipFile(file_name) as zf:
            with zf.open('csvs/card.csv') as f:
                try:
                    pre_card_data = list(csv.DictReader(io.TextIOWrapper(f, 'utf-8'), delimiter='\t'))
                except Exception as e:
                    raise Exception(f'unable to parse card CSV content - {e}')
            with zf.open('csvs/set.csv') as f:
                try:
                    pre_set_data = list(csv.DictReader(io.TextIOWrapper(f, 'utf-8'), delimiter='\t'))
                except Exception as e:
                    raise Exception(f'unable to parse set CSV content - {e}')
        # 3. Parse card data.
        card_data: list[Card] = []
        for entry in pre_card_data:
            try:
                keywords_data = _parse_keywords(
                    abilities_and_effects_str = entry['Abilities and Effects'],
                    abilities_and_effects_keywords_str = entry['Ability and Effect Keywords'],
                    body = entry['Functional Text'],
                    card_keywords_str = entry['Card Keywords'],
                    granted_keywords_str = entry['Granted Keywords']
                )
                types_data = _parse_types(entry['Types'])
                variations_data = _parse_variations(entry['Identifiers'], entry['Rarity'], entry['Variations'])
                card_data.append(Card(
                    ability_keywords = keywords_data['ability_keywords'],
                    art_types = variations_data['art_types'],
                    body = _parse_markdown_text(entry['Functional Text']),
                    card_type = cast(str, types_data['card_type']),
                    class_type = cast(Optional[str], types_data['class_type']),
                    cost = _parse_value(entry['Cost']),
                    defense = _parse_value(entry['Defense']),
                    effect_keywords = keywords_data['effect_keywords'],
                    editions = variations_data['editions'],
                    flavor_text = _parse_markdown_text(entry['Flavor Text']),
                    foilings = variations_data['foilings'],
                    full_name = _parse_full_name(entry['Name'], entry['Pitch']),
                    grants_keywords = keywords_data['grants_keywords'],
                    identifiers = variations_data['identifiers'],
                    image_urls = _parse_image_urls(entry['Image URLs']),
                    intellect = _parse_value(entry['Intelligence']),
                    keywords = keywords_data['keywords'],
                    label_keywords = keywords_data['label_keywords'],
                    legality = _parse_legality(entry),
                    life = _parse_value(entry['Health']),
                    name = entry['Name'].strip(),
                    pitch = _parse_value(entry['Pitch']),
                    power = _parse_value(entry['Power']),
                    rarities = variations_data['rarities'],
                    sets = [s.strip() for s in entry['Set Identifiers'].split(',')],
                    subtypes = cast(list[str], types_data['subtypes']),
                    supertypes = cast(list[str], types_data['supertypes']),
                    talent_type = cast(Optional[str], types_data['talent_type']),
                    token_keywords = keywords_data['token_keywords'],
                    types = cast(list[str], types_data['types']),
                    type_keywords = keywords_data['type_keywords'],
                    type_text = unidecode(entry['Type Text'].strip()),
                    variations = variations_data['variations']
                ))
            except Exception as e:
                raise Exception(f'unable to parse intermediate card data - {e} - {entry}')
        # 4. Parse set data.
        set_data: list[CardSet] = []
        for entry in pre_set_data:
            try:
                # Because of unicode:
                collectors_key = [k for k in entry.keys() if ('Collect' in k)][0]
                edition_data = _parse_set_edition_data(
                    editions_str = entry['Editions'],
                    irds_str = entry['Initial Release Dates'],
                    oopds_str = entry['Out of Print Dates'],
                    pp_str = entry['Product Pages'],
                    cc_str = entry[collectors_key],
                    cg_str = entry['Card Galleries']
                )
                set_data.append(CardSet(
                    dates = edition_data['dates'],
                    editions = edition_data['editions'],
                    identifier = entry['Identifier'].strip(),
                    id_range = _parse_set_start_end_id(entry['Start Card Id'], entry['End Card Id']),
                    name = unidecode(entry['Name']).strip(),
                    urls = edition_data['urls']
                ))
            except Exception as e:
                raise Exception(f'unable to parse intermediate card set data - {e} - {entry}')
        # 5. Initialize the card catalog.
        catalog = CardCatalog(card_data, set_data)
        if set_default:
            global DEFAULT_CATALOG
            DEFAULT_CATALOG = catalog
        # 6. Delete the temporary file.
        os.remove(file_name)
        # 7. Return result.
        return catalog

    @staticmethod
    def load(path: Optional[str] = None, set_default: bool = True) -> CardCatalog:
        '''
        Loads a card catalog from the specified source.

        If `path` is `None`, this method will load the data by fetching it
        remotely from the latest release of this module's GitHub repository.
        Otherwise, the specified path may be either a URL to a remote `.json`
        file, or a path to a `.json` file on the local machine. If the URL or
        local path end in `.gz`, the file will be automatically decompressed.

        Args:
          path: A URL or path to a remote or local `.json` file to parse.
          set_default: Whether to set the loaded catalog as the global default catalog.

        Returns:
          A new card catalog from the parsed data.
        '''
        if path is None:
            catalog = CardCatalog.load(f'{DEFAULT_BASE_URL}/latest/card-catalog.json.gz', set_default=False)
        elif path.startswith('http://') or path.startswith('https://'):
            with tempfile.NamedTemporaryFile(
                    prefix = 'fab-',
                    suffix = '.json.gz' if path.endswith('.gz') else '.json',
                    delete = False
            ) as f:
                f.write(requests.get(path).content)
                file_name = f.name
            catalog = CardCatalog.load(file_name, set_default=False)
        else:
            if path.endswith('.gz'):
                with gzip.open(os.path.expanduser(path), 'rt') as f:
                    catalog = CardCatalog.from_json(f.read())
            else:
                with open(os.path.expanduser(path), 'r') as f:
                    catalog = CardCatalog.from_json(f.read())
        if set_default:
            global DEFAULT_CATALOG
            DEFAULT_CATALOG = catalog
        return catalog

    def lookup_card(self, full_name: Optional[str] = None, identifier: Optional[str] = None, variation: Optional[str] = None) -> Card:
        '''
        Gets a single card by full name, identifier, or variation code.

        Args:
          full_name: The full name of the card to search for.
          identifier: The identifier string of the card to search for.
          variation: The variation code of the card to search for.

        Returns:
          A `Card` object from the catalog which matches the search query.
        '''
        if not identifier is None:
            return self.card_data[self.card_identifier_mapping[identifier]]
        elif not full_name is None:
            return self.card_data[self.card_full_name_mapping[full_name]]
        elif not variation is None:
            return self.card_data[self.card_variation_mapping[variation]]
        else:
            raise Exception('please specify a value for either `full_name`, `identifier`, or `variation`')

    def lookup_cards(self, key: str, value: Optional[int | str]) -> CardList:
        '''
        Gets all cards matching the specified requirement.

        The first time a particular key is used, an index mapping will be
        generated such that subsequent calls are faster.

        Args:
          key: The name of the card field to search for.
          value: The value associated with the card field.
        '''
        if not key in self.card_mapping_cache or not self.card_mapping_cache[key]:
            self.recompute_card_mapping_cache(key)
        indices = self.card_mapping_cache[key][value]
        return CardList(self.card_data[i] for i in indices)

    def lookup_set(self, identifier: Optional[str] = None, name: Optional[str] = None) -> CardSet:
        '''
        Gets a single card set by identifier or name.

        Args:
          identifier: The identifier code of the card set to search for.
          name: The name of the card set to search for.
        '''
        if not identifier is None:
            return self.set_data[self.set_identifier_mapping[identifier]]
        elif not name is None:
            return self.set_data[self.set_name_mapping[name]]
        else:
            raise Exception('please specify a value for either `name` or `identifier`')

    def recompute_base_mapping(self) -> None:
        '''
        Recomputes the base mappings (by identifier and full name) for this
        catalog.
        '''
        card_full_name_mapping = {}
        card_identifier_mapping = {}
        card_variation_mapping = {}
        set_identifier_mapping = {}
        set_name_mapping = {}
        for i, card in enumerate(self.card_data):
            card_full_name_mapping[card.full_name] = i
            for identifier in card.identifiers:
                card_identifier_mapping[identifier] = i
            for variation in card.variations:
                card_variation_mapping[variation] = i
        for i, card_set in enumerate(self.set_data):
            set_identifier_mapping[card_set.identifier] = i
            set_name_mapping[card_set.name] = i
        self.card_full_name_mapping = card_full_name_mapping
        self.card_identifier_mapping = card_identifier_mapping
        self.card_variation_mapping = card_variation_mapping
        self.set_identifier_mapping = set_identifier_mapping
        self.set_name_mapping = set_name_mapping

    def recompute_card_mapping_cache(self, key: str) -> None:
        '''
        Recomputes the card mapping cache for the specified key, allowing future
        lookups regarding that key to be quicker.

        Args:
          key: The key corresponding to the `Card` field to cache.
        '''
        new = {}
        for i, card in enumerate(self.card_data):
            if key in VALUE_FIELDS:
                value = cast(Optional[int | str], card[key])
                if value in new:
                    new[value].append(i)
                else:
                    new[value] = [i]
            elif key in STRING_LIST_FIELDS:
                value = cast(list[str], card[key])
                for subvalue in value:
                    if subvalue in new:
                        new[subvalue].append(i)
                    else:
                        new[subvalue] = [i]
            elif key in STRING_FIELDS:
                value = cast(Optional[str], card[key])
                if value in new:
                    new[value].append(i)
                else:
                    new[value] = [i]
            else:
                raise Exception(f'unsupported cache key "{key}"')
        self.card_mapping_cache[key] = new

    def save(self, file_path: str) -> None:
        '''
        Saves the card catalog to the specified `.json` file path.

        If the specified file path ends in `.gz`, the resulting file will be
        automatically compressed. This is recommended for catalogs that contain
        all cards in the game.

        Args:
          file_path: The `.json` file path to save the card catalog to.
        '''
        if not file_path.endswith('.json') and not file_path.endswith('.json.gz'):
            raise Exception('specified file path is not a JSON file')
        if file_path.endswith('.gz'):
            with gzip.open(os.path.expanduser(file_path), 'wt') as f:
                f.write(self.to_json())
        else:
            with open(os.path.expanduser(file_path), 'w') as f:
                f.write(self.to_json())

    def set_as_default(self) -> None:
        '''
        Sets this card catalog as the default card catalog.

        This may be used to dynamically switch between card catalogs.
        '''
        global DEFAULT_CATALOG
        DEFAULT_CATALOG = self

    def sets(self) -> list[CardSet]:
        '''
        Returns the list of all card sets contained within the catalog.

        Returns:
          The list of all card sets contained within the catalog.
        '''
        return self.set_data

    def to_dict(self) -> dict[str, list[dict]]:
        '''
        Converts this card catalog into a raw dictionary representation.

        Returns:
          The dictionary representation of the card catalog.
        '''
        return {
            'card_data': [card.to_dict() for card in self.card_data],
            'set_data': [s.to_dict() for s in self.set_data]
        }

    def to_json(self) -> str:
        '''
        Converts this card catalog into its JSON string representation.

        Returns:
          The JSON string representation of the card catalog.
        '''
        return json.dumps(self.to_dict())
