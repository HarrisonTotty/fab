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

from .card import CardList
from .card_set import CardSetCollection

STAT_TITLE = {
    'count': 'Number of Cards',
    'max_cost': 'Maximum Cost',
    'max_defense': 'Maximum Defense',
    'max_health': 'Maximum Health',
    'max_intelligence': 'Maximum Intelligence',
    'max_pitch': 'Maximum Pitch Value',
    'max_power': 'Maximum Power',
    'mean_cost': 'Mean Cost',
    'mean_defense': 'Mean Defense',
    'mean_health': 'Mean Health',
    'mean_intelligence': 'Mean Intelligence',
    'mean_pitch': 'Mean Pitch Value',
    'mean_power': 'Mean Power',
    'median_cost': 'Median Cost',
    'median_defense': 'Median Defense',
    'median_health': 'Median Health',
    'median_intelligence': 'Median Intelligence',
    'median_pitch': 'Median Pitch Value',
    'median_power': 'Median Power',
    'min_cost': 'Minimum Cost',
    'min_defense': 'Minimum Defense',
    'min_health': 'Minimum Health',
    'min_intelligence': 'Minimum Intelligence',
    'min_pitch': 'Minimum Pitch Value',
    'min_power': 'Minimum Power',
    'stdev_cost': 'Standard Deviation Cost',
    'stdev_defense': 'Standard Deviation Defense',
    'stdev_health': 'Standard Deviation Health',
    'stdev_intelligence': 'Standard Deviation Intelligence',
    'stdev_pitch': 'Standard Deviation Pitch Value',
    'stdev_power': 'Standard Deviation Power',
    'total_cost': 'Total Cost',
    'total_defense': 'Total Defense',
    'total_health': 'Total Health',
    'total_intelligence': 'Total Intelligence',
    'total_pitch': 'Total Pitch Value',
    'total_power': 'Total Power'
}

VALUE_TITLE = {
    'cost': 'Card Cost',
    'defense': 'Defense Value',
    'health': 'Health',
    'intelligence': 'Intelligence',
    'pitch': 'Pitch Value',
    'power': 'Power Value'
}

def distribution_plot(
    cards: CardList,
    bin_size: Optional[int] = 1,
    by: str = 'keyword',
    title: Optional[str] = None,
    value: str = 'power'
) -> Any:
    '''
    Produces a layered histogram of the specified
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
        layers = subcards.grants()
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
    elif by == 'keyword':
        layers = subcards.keywords()
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
    elif by == 'rarity':
        layers = subcards.rarities()
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
    elif by == 'type':
        layers = subcards.types()
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
        curve_type = 'normal'
    )
    fig.update_layout(
        title = title,
        xaxis_title = VALUE_TITLE[value],
        yaxis_title = 'Proportion'
    )
    return fig


def statistic_plot(
    cards: CardList,
    card_sets: CardSetCollection,
    statistic: str = 'median_power',
    style: str = 'lines',
    title: Optional[str] = None
) -> Any:
    '''
    Produces a graphical plot of the specified statistic over time. The
    specified statistic may be any key returned by the `CardList.statistics()`
    method. Ensure that the value for `card_sets` is the set of _all_ card sets.
    Accepts the following arguments:
      * statistic
        The specified statistic to plot on the y-axis.
      * style
        The plotting style of the function, being `lines`, `markers`, or
        `lines+markers`.
      * title
        An optional title for the plot.
    '''
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
