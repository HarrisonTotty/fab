# Flesh and Blood TCG Analysis Library

This site serves the API documentation for the `fab` Python module.

## Importing Card Data

```python
from fab import CardList, CardSetCollection

cards = CardList.load('data/cards.json', set_catalog=True)
card_sets = CardSetCollection.load('data/card-sets.json', set_catalog=True)
```
     
## Working With Card Data

See the [Getting Started Notebook](https://github.com/HarrisonTotty/fab/blob/main/notebooks/getting-started.ipynb).
