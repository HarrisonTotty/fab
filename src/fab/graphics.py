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

from .card import Card, STRING_FIELDS, STRING_LIST_FIELDS, VALUE_FIELDS
from .card_list import CardList

def _compute_hovertext(cards: CardList, limit: int = 4) -> str:
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

def _compute_stat_name(field: str, function: str) -> str:
    '''
    A helper function for computing the field+stat title name.
    '''
    FUNCMAP = {
        'max': 'Maximum',
        'mean': 'Mean',
        'median': 'Median',
        'stdev': 'Standard Deviation',
        'total': 'Total'
    }
    func_name = FUNCMAP[function]
    if field in VALUE_FIELDS:
        desc = VALUE_FIELDS[field]
    else:
        raise Exception(f'unknown field "{field}"')
    return f'{func_name} {desc}'

def distribution_plot(
    cards: CardList,
    group_by: str = 'class_type',
    group_values: list[str] = [],
    show_curve: bool = True,
    title: Optional[str] = None,
    value_field: str = 'power'
) -> Any:
    '''
    Produces a layered distribution plot of the specified list of cards,
    grouping with respect to a particular card field.

    If the specified `group_by` argument corresponds to a `Card` field of type
    `list[str]`, the list contents will be unpacked. Likewise, if the specified
    `value_field` argument corresponds to a `Card` field of type `list[str]`,
    then the taken "value" is assumed to be the number of elements of that list.

    Tip: Warning
      Card values which are not present (`None`) or variable (`'*'`) are not
      displayed.

    Args:
      cards: The list of cards to plot.
      group_by: The `Card` field to group the list of cards by.
      group_values: Limits the plotted groups to only the specified values.
      show_curve: Whether to include the normal curve in the plot.
      title: An optional title for the plot.
      value_field: The `Card` field from which to use for value comparison.

    Returns:
      A Plotly distribution plot of the data.
    '''
    groups = cards.group(by=group_by, include_none=False)


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
