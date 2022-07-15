'''
Contains the definitions associated with combat chains.
'''

from __future__ import annotations

import dataclasses

from collections import UserList
from typing import Any, Optional

from .card import Card, CardList

@dataclasses.dataclass
class ChainLink:
    '''
    Represents a particular link of the combat chain.

    Note:
      The following table describes the combat order and "owner" of each of the
      attributes of this object. Each of these attributes may correspond to a
      particular "step" in the link. See Chapter 7 of the _Comprehensive Rules_
      document for more information about these steps.

      | Order | Attribute               | Owner    | Allowed Card Types                  | Associated Step |
      |-------|-------------------------|----------|-------------------------------------|-----------------|
      | 0     | `pre_attack`            | Both     | _Action_ (for attacker), _Instant_  | Layer           |
      | 1     | `attack`                | Attacker | _Attack_, _Weapon_                  | Attack          |
      | 3     | `pre_defenses`          | Both     | _Instant_                           | Attack/Defend   |
      | 4     | `defenses`              | Defender | (cards with defense)                | Defend          |
      | 6     | `pre_attack_reaction`   | Both     | _Instant_                           | Reaction        |
      | 7     | `attack_reaction`       | Attacker | _Attack Reaction_                   | Reaction        |
      | 9     | `pre_defense_reaction`  | Both     | _Instant_                           | Reaction        |
      | 10    | `defense_reaction`      | Defender | _Defense Reaction_                  | Reaction        |
      | 11    | `post_defense_reaction` | Both     | _Instant_                           | Reaction        |

      Those attributes owned by both players take the form of an optional `list`
      of `tuple`s, where the first element of each `tuple` is a `str`
      representing the owner of the card in the second element, being either
      `attacker` or `defender`.

    Attributes:
      attack: The attack action card played in this the link.
      attack_reactions: Any attack reaction cards played in this link.
      defense_reactions: Any defense reaction cards played in this link.
      defenses: Any defending cards played in this link.
      post_defense_reaction: Any cards played after the defense reaction phase.
      pre_attack: Any cards played prior to the attacker playing an _Attack_ or _Weapon_ card.
      pre_attack_reaction: Any cards played by after the defending phase and prior to the attack reaction phase.
      pre_defense_reaction: Any cards played after the attack reaction phase and prior to the defense reaction phase.
      pre_defenses: Any cards played after the attack phase and prior to the defending phase.
    '''
    attack: Optional[Card] = None
    attack_reaction: Optional[Card] = None
    defense_reaction: Optional[Card] = None
    defenses: Optional[CardList] = None
    post_defense_reaction: Optional[list[tuple[str, Card]]] = None
    pre_attack: Optional[list[tuple[str, Card]]] = None
    pre_attack_reaction: Optional[list[tuple[str, Card]]] = None
    pre_defense_reaction: Optional[list[tuple[str, Card]]] = None
    pre_defenses: Optional[list[tuple[str, Card]]] = None


class CombatChain(UserList):
    '''
    Represents a FaB combat chain for a particular turn.

    Note:
      This is ultimately a superclass of `list`, and thus supports all common
      `list` methods.

    Attributes:
      data: The raw `list` of `ChainLink` objects contained within the object.
    '''
    data: list[ChainLink]

    def current_link(self) -> ChainLink:
        '''
        Gets the current link of the combat chain.

        Returns:
          A mutable reference to the current link of the combat chain.
        '''
        return self.data[-1]

    @staticmethod
    def empty() -> CombatChain:
        '''
        Creates a new empty combat chain.

        Returns:
          A new empty `CombatChain` object.
        '''
        return CombatChain([])
