'''
Contains definitions associated with plotting/drawing card data.
'''

import copy
import datetime
import statistics
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from typing import Any, Optional

from .card_list import CardList
from .card_set import CardSetCollection
from .deck import Deck

STAT_TITLE = {
    'count': 'Number of Cards',
    'max_cost': 'Maximum Cost',
    'max_defense': 'Maximum Defense',
    'max_intellect': 'Maximum Intellect',
    'max_life': 'Maximum Life',
    'max_pitch': 'Maximum Pitch Value',
    'max_power': 'Maximum Power',
    'mean_cost': 'Mean Cost',
    'mean_defense': 'Mean Defense',
    'mean_intellect': 'Mean Intellect',
    'mean_life': 'Mean Life',
    'mean_pitch': 'Mean Pitch Value',
    'mean_power': 'Mean Power',
    'median_cost': 'Median Cost',
    'median_defense': 'Median Defense',
    'median_intellect': 'Median Intellect',
    'median_life': 'Median Life',
    'median_pitch': 'Median Pitch Value',
    'median_power': 'Median Power',
    'min_cost': 'Minimum Cost',
    'min_defense': 'Minimum Defense',
    'min_intellect': 'Minimum Intellect',
    'min_life': 'Minimum Life',
    'min_pitch': 'Minimum Pitch Value',
    'min_power': 'Minimum Power',
    'num_blue': 'Number of Blue Cards',
    'num_red': 'Number of Red Cards',
    'num_yellow': 'Number of Yellow Cards',
    'pitch_cost_difference': 'Pitch-Cost Difference',
    'power_defense_difference': 'Power-Defense Difference',
    'stdev_cost': 'Standard Deviation Cost',
    'stdev_defense': 'Standard Deviation Defense',
    'stdev_intellect': 'Standard Deviation Intellect',
    'stdev_life': 'Standard Deviation Life',
    'stdev_pitch': 'Standard Deviation Pitch Value',
    'stdev_power': 'Standard Deviation Power',
    'total_cost': 'Total Cost',
    'total_defense': 'Total Defense',
    'total_intellect': 'Total Intellect',
    'total_life': 'Total Life',
    'total_pitch': 'Total Pitch Value',
    'total_power': 'Total Power'
}

VALUE_TITLE = {
    'body': 'Body Text',
    'cost': 'Resource Cost',
    'defense': 'Defense Value',
    'flavor_text': 'Flavor Text',
    'full_name': 'Full Name',
    'grants_keywords': 'Grants',
    'identifiers': 'Identifiers',
    'image_urls': 'Image URLs',
    'intellect': 'Intellect',
    'keywords': 'Keywords',
    'life': 'Life Value',
    'name': 'Name',
    'pitch': 'Pitch Value',
    'power': 'Power Value',
    'rarities': 'Rarities',
    'sets': 'Source Sets',
    'tags': 'Custom Tags',
    'type_text': 'Type Box Text',
    'types': 'Card Types'
}

def __compute_hovertext(cards: CardList, limit: int = 4) -> str:
    '''
    A handy function for computing hovertext for the specified list of cards.

    Args:
      cards: The list of cards to process.
      limit: The maximum number of card names to include per point.

    Returns:
      A hovertext string for the list of cards.
    '''
    if len(cards) > limit:
        remaining = len(cards) - (limit - 1)
        names = [card.name for card in cards[0:limit]] + [f'(+{remaining} more...)']
    else:
        names = [card.name for card in cards]
    return ' | '.join(names)

# def deck_distribution_plot(
#     decks: list[Deck],
#     bin_size: Optional[int] = 1,
#     show_curve: bool = True,
#     title: Optional[str] = None,
#     value: str = 'power'
# ) -> Any:
#     '''
#     '''

def distribution_plot(
    cards: CardList,
    bin_size: Optional[int] = 1,
    by: str = 'types',
    only: list[str] = [],
    show_curve: bool = True,
    title: Optional[str] = None,
    value: str = 'power'
) -> Any:
    '''
    Produces a layered distribution plot of the specified list of cards,
    grouping with respect to a particular card field.

    Tip: Warning
      Card values which are not present (`None`) or variable (`'*'`) are not
      displayed.

    Args:
      cards: The list of cards to plot.
      bin_size: An optional bin size (width of a single histogram column).
      by: The `Card` field to group by.
      only: An optional list of "groups" to restrict the results to.
      show_curve: Whether to display the normal curve in the resulting plot.
      title: An optional title string for the plot.
      value: The `Card` field to use as the value to compare between groups.

    Returns:
      A Plotly distribution plot of the data.

    Example:
      The following would create a plot to compare the distribution of power
      for all of the "hero classes".

      ```python
      from fab import CardList
      from fab import graphics as g
      from fab import meta

      cards = CardList.load('data/cards.json', set_catalog=True)

      g.distribution_plot(cards, by='types', only=meta.CLASS_TYPES, value='power')
      ```
    '''
    if value == 'cost':
        subcards = CardList([card for card in cards if isinstance(card.cost, int)])
    elif value == 'defense':
        subcards = CardList([card for card in cards if isinstance(card.defense, int)])
    elif value == 'health':
        subcards = CardList([card for card in cards if isinstance(card.health, int)])
    elif value == 'intelligence':
        subcards = CardList([card for card in cards if isinstance(card.intelligence, int)])
    elif value == 'pitch':
        subcards = CardList([card for card in cards if isinstance(card.pitch, int)])
    elif value == 'power':
        subcards = CardList([card for card in cards if isinstance(card.power, int)])
    else:
        raise Exception(f'unknown value {value}')
    if by == 'grants':
        layers = [l for l in subcards.grants() if not only or l in only]
        if value == 'cost':
            values = [[card.cost for card in subcards.filter(grants=layer) if isinstance(card.cost, int)] for layer in layers]
        elif value == 'defense':
            values = [[card.defense for card in subcards.filter(grants=layer) if isinstance(card.defense, int)] for layer in layers]
        elif value == 'health':
            values = [[card.health for card in subcards.filter(grants=layer) if isinstance(card.health, int)] for layer in layers]
        elif value == 'intelligence':
            values = [[card.intelligence for card in subcards.filter(grants=layer) if isinstance(card.intelligence, int)] for layer in layers]
        elif value == 'pitch':
            values = [[card.pitch for card in subcards.filter(grants=layer) if isinstance(card.pitch, int)] for layer in layers]
        elif value == 'power':
            values = [[card.power for card in subcards.filter(grants=layer) if isinstance(card.power, int)] for layer in layers]
        else:
            raise Exception(f'unknown value {value}')
    elif by in ['keyword', 'keywords']:
        layers = [l for l in subcards.keywords() if not only or l in only]
        if value == 'cost':
            values = [[card.cost for card in subcards.filter(keywords=layer) if isinstance(card.cost, int)] for layer in layers]
        elif value == 'defense':
            values = [[card.defense for card in subcards.filter(keywords=layer) if isinstance(card.defense, int)] for layer in layers]
        elif value == 'health':
            values = [[card.health for card in subcards.filter(keywords=layer) if isinstance(card.health, int)] for layer in layers]
        elif value == 'intelligence':
            values = [[card.intelligence for card in subcards.filter(keywords=layer) if isinstance(card.intelligence, int)] for layer in layers]
        elif value == 'pitch':
            values = [[card.pitch for card in subcards.filter(keywords=layer) if isinstance(card.pitch, int)] for layer in layers]
        elif value == 'power':
            values = [[card.power for card in subcards.filter(keywords=layer) if isinstance(card.power, int)] for layer in layers]
        else:
            raise Exception(f'unknown value {value}')
    elif by in ['rarity', 'rarities']:
        layers = [l for l in subcards.rarities() if not only or l in only]
        if value == 'cost':
            values = [[card.cost for card in subcards.filter(rarities=layer) if isinstance(card.cost, int)] for layer in layers]
        elif value == 'defense':
            values = [[card.defense for card in subcards.filter(rarities=layer) if isinstance(card.defense, int)] for layer in layers]
        elif value == 'health':
            values = [[card.health for card in subcards.filter(rarities=layer) if isinstance(card.health, int)] for layer in layers]
        elif value == 'intelligence':
            values = [[card.intelligence for card in subcards.filter(rarities=layer) if isinstance(card.intelligence, int)] for layer in layers]
        elif value == 'pitch':
            values = [[card.pitch for card in subcards.filter(rarities=layer) if isinstance(card.pitch, int)] for layer in layers]
        elif value == 'power':
            values = [[card.power for card in subcards.filter(rarities=layer) if isinstance(card.power, int)] for layer in layers]
        else:
            raise Exception(f'unknown value {value}')
    elif by in ['type', 'types']:
        layers = [l for l in subcards.types() if not only or l in only]
        if value == 'cost':
            values = [[card.cost for card in subcards.filter(types=layer) if isinstance(card.cost, int)] for layer in layers]
        elif value == 'defense':
            values = [[card.defense for card in subcards.filter(types=layer) if isinstance(card.defense, int)] for layer in layers]
        elif value == 'health':
            values = [[card.health for card in subcards.filter(types=layer) if isinstance(card.health, int)] for layer in layers]
        elif value == 'intelligence':
            values = [[card.intelligence for card in subcards.filter(types=layer) if isinstance(card.intelligence, int)] for layer in layers]
        elif value == 'pitch':
            values = [[card.pitch for card in subcards.filter(types=layer) if isinstance(card.pitch, int)] for layer in layers]
        elif value == 'power':
            values = [[card.power for card in subcards.filter(types=layer) if isinstance(card.power, int)] for layer in layers]
        else:
            raise Exception(f'unknown value {value}')
    else:
        raise Exception(f'unknown categorizer {by}')
    fig = ff.create_distplot(
        values,
        layers,
        bin_size = bin_size,
        curve_type = 'normal',
        show_curve = show_curve
    )
    fig.update_layout(
        title = title,
        xaxis_title = VALUE_TITLE[value],
        yaxis_title = 'Probability Density'
    )
    return fig


def pie_chart(
    cards: CardList,
    by: str = 'types',
    only: list[str] = [],
    statistic: str = 'count',
    title: Optional[str] = None
) -> Any:
    '''
    Produces a pie chart comparing the specified statistic between members of a
    certain grouping.

    Note:
      In general, only `int`-typed statistics produce meaningful representations
      in this kind of plot.

    Args:
      cards: The list of cards to plot.
      by: The `Card` field to group by, being `grants`, `keywords`, `rarities`, or `types`.
      only: Restricts the values specified in `by` to only displaying those specified.
      statistic: The `Card` statistic to consider the "value" of each slice. May be any statistic produced by `CardList.statistics()`.
      title: An optional title for the chart.

    Returns:
      A plotly pie chart figure.
    '''
    groups = cards.group(by=by)
    labels = []
    values = []
    for group_name, group_cards in groups.items():
        if only and not group_name in only: continue
        labels.append(group_name)
        values.append(group_cards.statistics()[statistic])
    fig = go.Figure(data=[go.Pie(
        labels = labels,
        values = values
    )])
    fig.update_layout(title=title)
    return fig


def scatter_plot(
    cards: CardList,
    x: str,
    y: str,
    by: Optional[str] = None,
    only: list[str] = [],
    title: Optional[str] = None
) -> Any:
    '''
    Produces a scatter plot comparing two `Card` fields in the specified list of
    cards.

    Tip: Warning
      Card values which are not present (`None`) or variable (`'*'`) are not
      displayed.

    Args:
      cards: The collection of cards to plot.
      x: The numerical `Card` field to plot on the x-axis.
      y: The numerical `Card` field to plot on the y-axis.
      by: An optional `Card` field to group by, being `grants`, `keywords`, `rarities`, or `types`.
      only: Restricts the values specified in `by` to only displaying those specified.
      title: An optional title for the plot.

    Returns:
      A Plotly scatter plot figure representing the data.

    Example:
      The following example would produce a scatterplot of card attack power
      over defense, with each card type color-coded.

      ```python
      from fab import CardList
      from fab import graphics as g

      cards = CardList.load('data/cards.json', set_catalog=True)

      fig = g.scatter_plot(cards, x='defense', y='power', by='types')
      fig.show()
      ```
    '''
    fig = go.Figure()
    num_traces = 0
    grouped_data = cards.group(by=by) if not by is None else {'all': cards}
    for category, data in grouped_data.items():
        if only and not category in only: continue
        xydata: list[tuple[int, int]] = list(set(
            (card[x], card[y]) for card in data if isinstance(card[x], int) and isinstance(card[y], int)
        ))
        hovertexts: list[str] = []
        for (xd, yd) in xydata:
            hovertexts.append(__compute_hovertext(
                data.filter(**{x: xd, y: yd})
            ))
        fig.add_trace(go.Scatter(
            hovertext = hovertexts,
            mode = 'markers',
            name = category,
            x = [d[0] for d in xydata],
            y = [d[1] for d in xydata]
        ))
        num_traces += 1
    fig.update_layout(
        showlegend  = num_traces > 1,
        title       = title,
        xaxis_title = VALUE_TITLE[x],
        yaxis_title = VALUE_TITLE[y]
    )
    return fig


def statistic_plot(
    cards: CardList,
    card_set_catalog: Optional[CardSetCollection] = None,
    statistic: str = 'median_power',
    style: str = 'lines',
    title: Optional[str] = None
) -> Any:
    '''
    Produces a graphical plot of the specified statistic over time.

    The specified statistic may be any key returned by the `CardList.statistics()`
    method.

    Note:
o      This plot requires a card set catalog to properly initialize cards.

    Args:
      cards: The list of cards to plot.
      card_set_catalog: An optional catalog to use instead of `card_set.CARD_SET_CATALOG`.
      statistic: The `Card` statistic to plot over time.
      style: The general style of the resulting plot, being `lines`, `markers`, or `lines+markers`.
      title: An optional title for the plot.

    Returns:
      A Plotly figure of the data.

    Example:
      The following would produce a scatterplot of the total defense of cards
      over time:

      ```python
      from fab import CardList, CardSetCatalog
      from fab import graphics as g

      cards = CardList.load('data/cards.json', set_catalog=True)
      card_Sets = CardSetCatalog.load('data/card-sets.json', set_catalog=True)

      fig = g.statistic_plot(cards, statistic='total_defense', style='markers')
      fig.show()
      ```
    '''
    card_sets = card_set_catalog if not card_set_catalog is None else card_set.CARD_SET_CATALOG
    if card_sets is None:
        raise Exception('specified card set catalog has not been initialized')
    fig = go.Figure()
    release_dates = sorted(card_sets.release_dates())
    stats = []
    for date in release_dates:
        stats.append(
            CardList([card for card in cards if card_sets.get_release_date(card) == date]).statistics()[statistic]
        )
    fig.add_trace(go.Scatter(
        mode = style,
        name = f'{STAT_TITLE[statistic]}',
        x = release_dates,
        y = stats,
    ))
    fig.update_layout(
        showlegend = False,
        title = title,
        xaxis_title = 'Date',
        yaxis_title = STAT_TITLE[statistic]
    )
    return fig


def table(cards: CardList, columns: list[str] = ['name', 'type_text', 'cost', 'defense', 'pitch', 'power', 'grants', 'keywords']) -> Any:
    '''
    Renders a table for the specified collection of cards.

    Args:
      cards: The collection of cards to render.
      columns: Specifies the list of columns to render, corresponding to `Card` object fields.

    Returns:
      A Plotly figure representing the table data.
    '''
    fig = go.Figure()
    cells = []
    for column in columns:
        c = [card[column] for card in cards]
        cells.append(c)
    fig.add_trace(go.Table(
        header = {
            'align': 'left',
            'values': [VALUE_TITLE[column] for column in columns],
        },
        cells = {
            'align': 'left',
            'values': cells
        }
    ))
    return fig
