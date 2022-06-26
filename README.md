![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/HarrisonTotty/fab?include_prereleases&style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/HarrisonTotty/fab?style=flat-square)
![Read the Docs](https://img.shields.io/readthedocs/fablib?style=flat-square)

# Flesh and Blood TCG Analysis Environment

A Python library and [Jupyter Lab](https://jupyter.org/) environment for
analysis of the Flesh and Blood trading card game. Card data powered by
[flesh-cube/flesh-and-blood-cards](https://github.com/flesh-cube/flesh-and-blood-cards).


## Getting Started

In short, there are basically two ways you can start using `fab`: either
downloading and installing the latest release `.whl` via `pip`, _or_ building
and running the containerized Jupyter Lab environment.

To learn more about working with the library, check out the [Getting
Started](notebooks/getting-started.ipynb) notebook or the [Online API
Documentation](https://fablib.readthedocs.io/en/latest/).

### Installing Locally

```bash
export VERSION=0.1.9
curl "https://github.com/HarrisonTotty/fab/releases/download/v${VERSION}/fab-${VERSION}-py3-none-any.whl" -o fab.whl
pip install fab.whl
```

### Building & Running Container Image

``` bash
./build-env.sh && ./run-env.sh
```

(then navigate to `http://127.0.0.1:8888/lab`)


## Card Objects

The core functionality of `fab` centers around `Card` objects. A `Card` is a
[dataclass](https://docs.python.org/3/library/dataclasses.html) that represents
any unique Flesh and Blood trading card. It should be noted here that this
library treats all reprints, alternative artworks, and foiling under the same
`Card`. Each `Card` contains the following fields:

| Field Name     | Data Type               | Description                                                                    |
|----------------|-------------------------|--------------------------------------------------------------------------------|
| `body`         | `str` or `None`         | The full body text of the card, excluding flavor text.                         |
| `cost`         | `int`, `str`, or `None` | The cost of the card (how much you need to pitch).                             |
| `defense`      | `int`, `str`, or `None` | The defense value of the card.                                                 |
| `flavor_text`  | `str` or `None`         | Any lore text printed on the card.                                             |
| `full_name`    | `str`                   | The name of the card, including its pitch value.                               |
| `grants`       | `list[str]`             | A list of key words this card grants to _other cards_.                         |
| `health`       | `int` or `None`         | The health value of this card (for heroes and minions).                        |
| `identifiers`  | `list[str]`             | A list of card identifiers, such as `RNR012`.                                  |
| `image_urls`   | `list[str]`             | A list of card image URLs.                                                     |
| `intelligence` | `int` or `None`         | The intelligence value of the card (for heroes).                               |
| `keywords`     | `list[str]`             | A list of key words associated with this card, such as `Dominate`.             |
| `name`         | `str`                   | The name of this card, excluding pitch value.                                  |
| `pitch`        | `int` or `None`         | The pitch value of the card.                                                   |
| `power`        | `int`, `str`, or `None` | The power (attack) value of the card.                                          |
| `rarities`     | `list[str]`             | A list of rarities available to this card, corresponding to each identifier.   |
| `sets`         | `list[str]`             | The list of card set codes associated with this card.                          |
| `tags`         | `list[str]`             | A collection of user-defined tags that can be used to filter out cards.        |
| `type_text`    | `str`                   | The full type text at the bottom of the card, such as `Ninja Action - Attack`. |
| `types`        | `list[str]`             | The list of types contained within this card's type text.                      |

A value of `None` for any of the above fields indicates that the field is not
present on the card (for example `health` is `None` for most cards except for
heroes). Similarly, a `str` value for a normally numeric field indicates cards
that may have values dependent on a condition in their body text. A typical
`Card` object might look like the following:

```python
from fab import Card

card = Card(
  body         = 'Your next weapon attack this turn gains +1{p}.\n\n**Go again**',
  cost         = 0,
  defense      = 3,
  flavor_text  = None,
  full_name    = 'Sharpen Steel (3)',
  grants       = [],
  health       = None,
  identifiers  = ['TEA024', 'WTR143'],
  image_urls   = ['https://...', 'https://...', 'https://...'],
  intelligence = None,
  keywords     = ['Go again'],
  name         = 'Sharpen Steel',
  pitch        = 3,
  power        = None,
  rarities     = ['C', 'C'],
  sets         = ['TEA', 'WTR'],
  tags         = [],
  type_text    = 'Warrior Action',
  types        = ['Warrior', 'Action']
)
```

It should be noted that manually defining a `Card` object this way is not the
usual workflow for working with them. In most cases, what you _actually_ want to
do is load _all possible_ cards from a `.csv` or `.json` file into a `CardList`
object. `CardList` objects are basically `list[Card]` but with may additional
convenience methods for filtering, grouping, and sorting cards. The following
provides a breif overview of some of the things you can do:

```python
from fab import CardList

# First, let's load in all the cards in the game.
cards = CardList.load('data/cards.json', set_catalog=True)

# As you'd expect, card lists can be iterated over:
for card in cards:
  print(card.name)
  
# Let's think about cards that might work in a Chane deck. We can start by
# filtering the cards down to what we want to work with.
compatible = cards.filter(types=['Generic', 'Shadow', 'Runeblade'])

# What are some high power runeblade cards that pitch for two or three
# resources?
answer = compatible.filter(types = 'Runeblade', pitch = (2,3)).sort(key = 'power', reverse = True)

# What is the average defense of each card type in the game?
averages = {k: v.mean_defense() for k, v in cards.group(by = 'type').items()}
```


## Card Decks

`fab` also provides utilities to create and analyze card decks via the `Deck`
object. Each `Deck` object contains the following fields:

| Field Name  | Data Type  | Description                                                                            |
|-------------|------------|----------------------------------------------------------------------------------------|
| `cards`     | `CardList` | The list of cards that make up the "main" part of the deck (that you draw from).       |
| `format`    | `str`      | The game format associated with the deck (such as `Blitz`).                            |
| `hero`      | `Card`     | The hero card associated with the deck.                                                |
| `inventory` | `CardList` | The list of equipment and weapon cards associated with the deck (not including items). |
| `name`      | `str`      | An arbitrary name for the deck.                                                        |
| `tokens`    | `CardList` | Any token cards used by the deck.                                                      |

`Deck` objects provide a variety of useful methods - from being able to compute
scoped card statistics, to generating deck lists. You can also validate whether
the deck is valid (legal) for the specified game format.


## Project Status

This project is still really early in development. It's code is mostly based on
a personal finance platform I wrote called
[tcat](https://github.com/HarrisonTotty/tcat) and is pretty opinionated. However
if you want to contribute to the project, feel free to reach out to me. I
imagine contribution requirements will morph as/if the project gets bigger.
