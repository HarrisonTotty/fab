'''
Contains the definition of an _Object_ in Flesh and Blood, as defined in section
_1.2_ of the _Comprehensive Rules_ document.
'''

from __future__ import annotations

from typing import Any, Optional

class FaBObject:
    '''
    Represents an _Object_ in Flesh and Blood, as defined in section _1.2_ of
    the _Comprehensive Rules_ document.

    Attributes:
      controller: The object or player name
      identities: The list of identities the object may be referred to.
      permanent: Whether this object is designated as a _permanent_.
    '''
    controller: Optional[FaBObject | str] = None
    identities: set[str] = {'object'}
    owner: Optional[FaBObject | str] = None
    permanent: bool = False
    properties: dict[str, Any] = {}
