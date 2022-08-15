# Flesh and Blood TCG Analysis Library

This site serves the API documentation for the `fab` Python module.

## Quick Start

```python
from fab import *

catalog = CardCatalog.load()
```

## TL;DR `fab` Object Guide

The following table provides a brief description of the major objects in this
module.

| Name            | Description                                                                    | Inherits                                                                            |
|-----------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `Card`          | A generic representation of any Flesh and Blood card by full name.             | `CardBase`                                                                          |
| `CardBase`      | An abstract class from which `Card` and `CardVariant` objects are built.       | [dataclass](https://docs.python.org/3/library/dataclasses.html)                     |
| `CardCatalog`   | An organized catalog of all cards in the game.                                 |                                                                                     |
| `CardInventory` | An organizer for users to keep track of what cards they own.                   | [UserDict](https://docs.python.org/3/library/collections.html#collections.UserDict) |
| `CardList`      | A list of `Card` objects, with some helpful methods.                           | [UserList](https://docs.python.org/3/library/collections.html#collections.UserList) |
| `CardSet`       | Contains data on a particular card box set (such as "Uprising").               | [dataclass](https://docs.python.org/3/library/dataclasses.html)                     |
| `CardVariant`   | A specific instance of a Flesh and Blood card (with unique id, foiling, etc).  | `CardBase`                                                                          |
| `Deck`          | Represents a deck of cards, with associated metadata (it's name, format, etc). | [dataclass](https://docs.python.org/3/library/dataclasses.html)                     |
| `PlayerProfile` | Represents a player's official FaB record (Gem ID).                            | [dataclass](https://docs.python.org/3/library/dataclasses.html)                     |
     
## Working With Card Data

See the [Getting Started Notebook](https://github.com/HarrisonTotty/fab/blob/main/notebooks/getting-started.ipynb).
