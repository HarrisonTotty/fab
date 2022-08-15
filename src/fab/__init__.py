'''
Flesh and Blood TCG Analysis Platform

A python library for analyzing the Flesh and Blood trading card game.
'''

__VERSION__ = "0.4.0"

from . import graphics
from . import meta
from .card import Card
from .card_base import CardBase
from .card_catalog import CardCatalog
from .card_inventory import CardInventory
from .card_list import CardList
from .card_set import CardSet
from .card_variant import CardVariant
from .deck import Deck
from .gemid import PlayerProfile
