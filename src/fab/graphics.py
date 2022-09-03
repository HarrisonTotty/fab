'''
Contains definitions associated with plotting/drawing card data.
'''

import networkx as nx
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

from pandas import DataFrame
from typing import Any, Callable, cast, Optional

from .card import STRING_FIELDS, STRING_LIST_FIELDS, VALUE_FIELDS, Card
from .card_list import CardList

TYPE_COLORS = {
    # Classes
    'Adjudicator': 'burlywood',
    'Bard': 'silver',
    'Brute': 'green',
    'Guardian': 'blue',
    'Illusionist': 'lavender',
    'Mechanologist': 'orange',
    'Merchant': 'gold',
    'Ninja': 'lime',
    'Ranger': 'brown',
    'Runeblade': 'purple',
    'Shapeshifter': 'pink',
    'Warrior': 'red',
    'Wizard': 'cyan',
    # Talents
    'Draconic': 'red',
    'Earth': 'green',
    'Elemental': 'lavender',
    'Ice': 'cyan',
    'Lightning': 'yellow',
    'Shadow': 'purple'
}

def _networkx_to_plotly(
        edges: list[tuple[int | str, int | str, dict[str, Any]]],
        node_colors: dict[str, str],
        node_color_groups: dict[str, str],
        node_sizes: dict[str, int],
        node_symbol_groups: dict[str, str],
        height: int = 960,
        layout: str ='spring',
        line_color: str = 'gray',
        line_width: float = 0.5,
        show_legend = True,
        title: Optional[str] = None,
        width: int = 1280
) -> go.Figure:
    '''
    A helper function for converting networkx graphs into plotly figures.
    '''
    graph = nx.Graph()
    graph.add_edges_from(edges)
    if layout == 'spring':
        layout_pos = nx.spring_layout(graph)
    elif layout == 'shell':
        layout_pos = nx.shell_layout(graph)
    elif layout == 'planar':
        layout_pos = nx.planar_layout(graph)
    else:
        raise ValueError(f'unknown layout "{layout}"')
    node_data_raw = [{'name': k, 'x': v[0], 'y': v[1], 'color': node_colors.get(k, 'black'), 'color_group': node_color_groups.get(k, 'Other'), 'size': node_sizes.get(k, 5), 'symbol_group': node_symbol_groups.get(k, 'Other')} for k, v in layout_pos.items()]
    node_data = DataFrame(node_data_raw)
    nodes_trace = px.scatter(
        node_data,
        color = 'color_group',
        color_discrete_map = {n['color_group']: n['color'] for n in node_data_raw} if node_colors else None,
        hover_data = ['color_group', 'size', 'symbol_group'],
        hover_name = 'name',
        size = 'size',
        symbol = 'symbol_group' if node_symbol_groups else None,
        x = 'x',
        y = 'y'
    )
    edge_data = {'x': [], 'y': []}
    for n1, n2, _ in edges:
        n1d = [n for n in node_data_raw if n['name'] == n1][0]
        n2d = [n for n in node_data_raw if n['name'] == n2][0]
        for a in ['x', 'y']:
            edge_data[a] += [n1d[a], n2d[a], None]
    edges_trace = go.Scatter(
        hoverinfo = 'none',
        line = {'color': line_color, 'width': line_width},
        mode = 'lines',
        name = 'Edges',
        showlegend = False,
        x = edge_data['x'],
        y = edge_data['y']
    )
    fig_layout = go.Layout(
        height = height,
        hovermode = 'closest',
        showlegend = show_legend,
        title = title,
        width = width,
    )
    fig = go.Figure(data=[edges_trace], layout=fig_layout)
    fig.add_traces(nodes_trace.data)
    fig.update_layout(plot_bgcolor = 'white')
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def box_plot(
    cards: CardList,
    color_field: str = 'class_types',
    title: Optional[str] = None,
    x_field: str = 'talent_types',
    y_field: str = 'power'
) -> go.Figure:
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
    df = cards.to_flat_dataframe(fields=[color_field, x_field])
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
    group_by: str = 'class_types',
    group_values: list[str] = [],
    show_curve: bool = True,
    title: Optional[str] = None,
    value_field: str = 'power'
) -> go.Figure:
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

def relationship_graph(
    cards: CardList,
    edge_function: Callable[[Card, Card], bool | int],
    color_group_function: Optional[Callable[[Card], str]] = None,
    height: int = 960,
    layout: str = 'spring',
    node_function: Optional[Callable[[Card], str]] = None,
    size_function: Optional[Callable[[Card], int]] = None,
    symbol_group_function: Optional[Callable[[Card], str]] = None,
    title: Optional[str] = None,
    width: int = 1280
) -> go.Figure:
    '''
    Computes a relationship graph between cards.
    '''
    color_group_function = lambda card: 'Generic' if not card.class_types else ' '.join(card.class_types)
    if node_function is None: node_function = lambda card: card.name
    if size_function is None: size_function = lambda _: 10
    edges = []
    colors = {}
    color_groups = {}
    sizes = {}
    symbol_groups = {}
    for card in cards:
        for other in cards:
            if card.name == other.name: continue
            weight = edge_function(card, other)
            if weight:
                card_name = node_function(card)
                other_name = node_function(other)
                edges.append(
                    (card_name, other_name, {'weight': weight})
                )
                # if not card_name in colors and default_colors:
                #     colors[card_name] = TYPE_COLORS.get(color_group_function(card), 'black')
                if not card_name in color_groups:
                    color_groups[card_name] = color_group_function(card)
                if not card_name in sizes:
                    sizes[card_name] = size_function(card)
                if not card_name in symbol_groups and not symbol_group_function is None:
                    symbol_groups[card_name] = symbol_group_function(card)
                # if not other_name in colors and default_colors:
                #     colors[other_name] = TYPE_COLORS.get(color_group_function(card), 'black')
                if not other_name in color_groups:
                    color_groups[other_name] = color_group_function(other)
                if not other_name in sizes:
                    sizes[other_name] = size_function(other)
                if not other_name in symbol_groups and not symbol_group_function is None:
                    symbol_groups[other_name] = symbol_group_function(other)
    return _networkx_to_plotly(
        edges = edges,
        height = height,
        layout = layout,
        line_color = 'gray',
        line_width = 0.5,
        node_color_groups = color_groups,
        node_colors = colors,
        node_sizes = sizes,
        node_symbol_groups = symbol_groups,
        title = title,
        width = width
    )


def scatter_plot(
    cards: CardList,
    group_by: str = 'class_types',
    hover_fields: list[str] = [],
    title: Optional[str] = None,
    trendline: Optional[str] = None,
    x: str = 'cost',
    y: str = 'power'
) -> go.Figure:
    '''
    Creates a scatter plot comparing the specified card fields.

    Args:
      cards: The list of cards to plot.
      group_by: The `Card` field to group cards by.
      hover_fields: A list of additional `Card` fields to display on hover.
      title: An optional title for the plot.
      trendline: Specifies a trendline algorithm to plot for each group, being one of `ols`, `lowess`, `rolling`, `expanding`, or `ewm`.
      x: The `Card` field to display on the x-axis of the plot.
      y: The `Card` field to display on the y-axis of the plot.

    Returns:
      A Plotly `Figure` object representing the plot.
    '''
    if any(k in STRING_LIST_FIELDS for k in [x, y, group_by]):
        df = cards.to_flat_dataframe(fields=[k for k in [x, y, group_by] if k in STRING_LIST_FIELDS])
    else:
        df = cards.to_dataframe()
    titles = []
    for k in [x, y, group_by]:
        if k in STRING_FIELDS:
            titles.append(STRING_FIELDS[k])
        elif k in STRING_LIST_FIELDS:
            titles.append(STRING_LIST_FIELDS[k][1])
        elif k in VALUE_FIELDS:
            titles.append(VALUE_FIELDS[k])
        else:
            raise ValueError(f'specified field "{k}" is not supported')
    fig = px.scatter(
        df,
        color = group_by,
        hover_data = hover_fields if hover_fields else None,
        hover_name = 'name',
        trendline = trendline,
        x = x,
        y = y,
    )
    fig.update_layout(
        legend_title_text = titles[2],
        title = title,
        xaxis_title = titles[0],
        yaxis_title = titles[1],
    )
    return fig


def table(cards: CardList, hide: list[str] = ['intellect', 'life', 'pitch']) -> Any:
    '''
    Displays the specified list of cards in a table.

    This method does not display all card fields, but rather an opinionated
    subset of the most useful fields.

    Args:
      cards: The list of cards to display.
      hide: An optional list of additional card fields to hide.

    Returns:
      A table representation of the list of cards.
    '''
    ignore = [
        'dates',
        'image_urls',
        'legality',
        STRING_FIELDS['body'],
        STRING_FIELDS['flavor_text'],
        STRING_FIELDS['full_name'],
        STRING_FIELDS['notes'],
        STRING_LIST_FIELDS['art_types'][0],
        STRING_LIST_FIELDS['editions'][0],
        STRING_LIST_FIELDS['foilings'][0],
        STRING_LIST_FIELDS['keywords'][0],
        STRING_LIST_FIELDS['sets'][0],
        STRING_LIST_FIELDS['types'][0],
        STRING_LIST_FIELDS['variations'][0],
    ]
    for field in hide:
        if field in STRING_FIELDS:
            ignore.append(STRING_FIELDS[field])
        elif field in STRING_LIST_FIELDS:
            ignore.append(STRING_LIST_FIELDS[field][0])
        elif field in VALUE_FIELDS:
            ignore.append(VALUE_FIELDS[field])
        else:
            raise KeyError(f'unknown card field "{field}"')
    result = cards.to_dataframe()
    names = result['name']
    identifiers = result['identifiers']
    colors = result['color']
    result = cast(DataFrame, result.drop(columns=['name', 'identifiers', 'color']))
    result.insert(loc=0, column='Color', value=colors)
    result.insert(loc=0, column='Name', value=names)
    result.insert(loc=0, column='Identifiers', value=identifiers)
    result.rename(columns=STRING_FIELDS, inplace=True) # type: ignore
    result.rename(columns={k: v[0] for k,v in STRING_LIST_FIELDS.items()}, inplace=True) # type: ignore
    result.rename(columns=VALUE_FIELDS, inplace=True) # type: ignore
    return result.style.hide(ignore, axis='columns').hide()
