'''
Flesh and Blood TCG Analysis Platform

A python library for analyzing the Flesh and Blood trading card game.
'''

__VERSION__ = "0.2.1"

from . import graphics, meta
from .arena import Arena, PlayerSpace
from .card import Card, CardList
from .card_set import CardSet, CardSetCollection
from .chain import ChainLink, CombatChain
from .deck import Deck
