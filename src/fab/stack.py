'''
Contains the definition of the card _Stack_ and its associated _Layers_.
'''

from __future__ import annotations

import dataclasses

from collections import UserList
from typing import Any, Optional

@dataclasses.dataclass
class StackLayer:
    '''
    Represents a particular layer on the `Stack`.
    '''

class Stack(UserList):
    '''
    Represents a stack of layers.
    '''
    data: list[StackLayer]
