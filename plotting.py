import plotly.graph_objects as go
import numpy as np

def create_axes(figure):

    # x-axis
    figure.add_shape(
        type = "line",
        y0=0,
        y1=0,
        x0=0,
        x1=1,
        xref = "paper",
        line = dict(color = "white", width = 1)
    )

    # y-axis
    figure.add_shape(
        type = "line",
        y0=0,
        y1=1,
        x0=0,
        x1=0,
        yref = "paper",
        line = dict(color = "white", width = 1)
    )

def create_basic_option_graph(S, K, maximum_stock_value, maximum_strike_value, modelled_price, option_type):    

    x_prices = np.linspace(0, maximum_stock_value * 10, int(maximum_stock_value * 20))
    y_profit = []

    rel = maximum_strike_value / 25
    rel_input = max(S,K) / 5

    if option_type == "Call":  
        for x in x_prices:
            y_profit.append(max(x - K, 0) - modelled_price)
    else:
        for x in x_prices:
            y_profit.append(max(K - x, 0) - modelled_price)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = x_prices,
        y = y_profit,
        mode = "lines"
    ))

    create_axes(fig)    

    # Dashed lines placement [x, y]
    dashed_lines = [
        [K, max(x_prices)],
        [K + (modelled_price if option_type == "Call" else -modelled_price), max(x_prices)]
    ]

    # Put options are defined differently
    if option_type == "Put":
        dashed_lines[1][0] = K - modelled_price

    # Dashed lines
    for x, y in dashed_lines:     
        fig.add_shape(
            type="line",
            x0=x,
            x1=x,
            y0=-y,
            y1=y,
            line=dict(color="white", width=1, dash="dash"),
            xref="x",
            yref="y"
        )

    # names of axes and the size of the graph
    fig.update_layout(
        xaxis_title = "S(t)",
        yaxis_title = "Payoff (in €)",
        width = 100,
        height = 500,
    )

    # Annotation points added to the graph, mainly the important points like "C", "K", and the profit differential "K+C"

    relative_y_annotations = modelled_price / 10 + rel / 10

    if option_type == "Call":
        annotations = [
            [-(rel_input / 4), -modelled_price, "-C"],
            [K - rel_input / 3, relative_y_annotations, "K"],
            [K + modelled_price - rel_input / 2, relative_y_annotations, "K + C"]
        ]

        # If "K" dashed line is relatively close to the start x = 0, then move the letter "K" to the right,
        # so it doesn't touch the y-axis
        if K < rel_input:
            annotations[1][0] = K + rel_input / 3

        # If "K" is relatively close to "K + C", the annotation 'jumps' to the other side, so that they don't
        # intersect with eachother 
        if (K + modelled_price - K) < rel_input:
            annotations[2][0] = K + modelled_price + rel_input / 2

    else:
        annotations = [
            [-(rel_input / 4), -modelled_price, "-P"],
            [K + rel_input / 3, relative_y_annotations, "K"],
            [K - modelled_price + rel_input / 2, relative_y_annotations, "K - P"]
        ]   

        # If "K" is relatively close to "K + P", the annotation 'jumps' to the other side, so that they don't
        # intersect with eachother 
        if (K + modelled_price - K) < rel_input:
            annotations[2][0] = K - modelled_price - rel_input / 2

    for x, y, label in annotations:
        fig.add_annotation(
            x = x,
            y = y,
            text = label,
            showarrow = False,
            font = dict(size = 14)
        )

    # x and y axes are adjusted accordingly to the size and shape of the graph
    fig.update_xaxes(range = [-rel_input / 2.5, K + modelled_price + rel_input * 2.5])
    fig.update_yaxes(range = [-modelled_price-rel, modelled_price+rel])
    return(fig)