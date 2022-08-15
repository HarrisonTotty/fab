'''
Contains definitions associated with plotting/drawing card data.
'''

import copy
import datetime
import statistics
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

from typing import Any, cast, Optional

from .card import STRING_FIELDS, STRING_LIST_FIELDS, VALUE_FIELDS
from .card_list import CardList

# def _compute_hovertext(cards: CardList, limit: int = 4) -> str:
#     '''
#     A handy function for computing hovertext for the specified list of cards.

#     Args:
#       cards: The list of cards to process.
#       limit: The maximum number of card names to include per point.

#     Returns:
#       A hovertext string for the list of cards.
#     '''
#     if len(cards) > limit:
#         remaining = len(cards) - (limit - 1)
#         names = [card.name for card in cards[0:limit]] + [f'(+{remaining} more...)']
#     else:
#         names = [card.name for card in cards]
#     return ' | '.join(names)

# def _compute_stat_name(field: str, function: str) -> str:
#     '''
#     A helper function for computing the field+stat title name.
#     '''
#     FUNCMAP = {
#         'max': 'Maximum',
#         'mean': 'Mean',
#         'median': 'Median',
#         'stdev': 'Standard Deviation',
#         'total': 'Total'
#     }
#     func_name = FUNCMAP[function]
#     if field in VALUE_FIELDS:
#         desc = VALUE_FIELDS[field]
#     else:
#         raise Exception(f'unknown field "{field}"')
#     return f'{func_name} {desc}'

def box_plot(
    cards: CardList,
    color_field: str = 'class_type',
    title: Optional[str] = None,
    x_field: str = 'talent_type',
    y_field: str = 'power'
) -> Any:
    '''
    Produces a box plot of the specified list of cards.

    The box plot compares the range of values of a particular `Card` field on
    the Y-axis (`y_field`) for a given categorical field on the X-axis
    (`x_field`). These box plots are then divided and colored based on a third
    categorical field (`color_field`).

    Args:
      cards: The list of cards to plot.
      color_field: The `Card` field for which box colors should be assigned.
      title: An optional title for the plot.
      x_field: The categorical `Card` field to plot on the X-axis.
      y_field: The value-based `Card` field to plot on the Y-axis.

    Returns:
      A plotly figure object representing the plot.
    '''
    labels = {}
    df = cards.to_dataframe()
    if color_field in STRING_LIST_FIELDS:
        df.explode(color_field)
        labels[color_field] = STRING_LIST_FIELDS[color_field][1]
    elif color_field in STRING_FIELDS:
        labels[color_field] = STRING_FIELDS[color_field]
    else:
        raise ValueError('invalid color field')
    if x_field in STRING_LIST_FIELDS:
        df.explode(x_field)
        labels[x_field] = STRING_LIST_FIELDS[x_field][1]
    elif x_field in STRING_FIELDS:
        labels[x_field] = STRING_FIELDS[x_field]
    else:
        raise ValueError('invalid x-axis field')
    if y_field in VALUE_FIELDS:
        labels[y_field] = VALUE_FIELDS[y_field]
    else:
        raise ValueError('invalid y-axis field')
    fig = px.box(
        df.fillna('None'),
        color = color_field,
        labels = labels,
        title = title,
        x = x_field,
        y = y_field
    )
    fig.update_traces(quartilemethod='exclusive')
    return fig

def distribution_plot(
    cards: CardList,
    curve_type: str = 'kde',
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
      displayed. Any groups containing a single card will also not be displayed.

    Args:
      cards: The list of cards to plot.
      curve_type: The type of curve to plot if `show_curve` is set to `True`, being either `kde` or `normal`.
      group_by: The `Card` field to group the list of cards by.
      group_values: Limits the plotted groups to only the specified values.
      show_curve: Whether to include the normal curve in the plot.
      title: An optional title for the plot.
      value_field: The `Card` field from which to use for value comparison.

    Returns:
      A Plotly distribution plot of the data.
    '''
    initial_groups = cards.group(by=group_by, count_threshold=2, include_none=False)
    if value_field in VALUE_FIELDS:
        groups = {k: [c[value_field] for c in v if isinstance(c[value_field], int)] for k, v in initial_groups.items()}
        xaxis_title = VALUE_FIELDS[value_field]
    elif value_field in STRING_LIST_FIELDS:
        groups = {k: [len(cast(list[str], c[value_field])) for c in v] for k, v in initial_groups.items()}
        xaxis_title = STRING_LIST_FIELDS[value_field]
    else:
        raise ValueError(f'unsupported value field "{value_field}"')
    group_labels = [g for g, v in groups.items() if (not group_values or g in group_values) and len(v) >= 2]
    data = [v for g, v in groups.items() if g in group_labels]
    fig = ff.create_distplot(
        data,
        group_labels,
        bin_size = 1,
        curve_type = curve_type,
        show_curve = show_curve,
        show_rug = False
    )
    fig.update_layout(
        title = title,
        xaxis_title = xaxis_title,
        yaxis_title = 'Probability Density'
    )
    return fig

def table(cards: CardList) -> pd.Styler:
    '''
    Displays the specified list of cards in a table.

    This method does not display all card fields, but rather a subset of the
    most useful fields.

    Args:
      cards: The list of cards to display.

    Returns:
      A table representation of the list of cards.
    '''
    ignore = [
        'Body Text', 'Editions', 'Dates', 'Flavor Text', 'image_urls', 'legality', 'Types', 'Keywords', 'Notes', 'Full Name'
    ]
    result = cards.to_dataframe()
    result.replace(STRING_FIELDS, inplace=True)
    result.replace({k: v[0] for k,v in STRING_LIST_FIELDS.items()}, inplace=True)
    result.replace(VALUE_FIELDS, inplace=True)
    return result.style.hide(ignore, axis='columns')
