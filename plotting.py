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

def get_annotations(K, option_type, modelled_price, rel_x_pos, rel_y_pos):
    # Annotation points added to the graph, mainly the important points like "C", "K", and the profit differential "K+C"

    if option_type == "Call":
        annotations = [
            [-rel_x_pos, -modelled_price, "-C"],
            [K - rel_x_pos, rel_y_pos, "K"],
            [K + modelled_price - rel_x_pos * 1.5, rel_y_pos, "K + C"]
        ] # As the "K + C" is inherently larger than a single letter, we have to align them more agressively (reason for * 1.5)

        # If "K" dashed line is relatively close to the start x = 0, then move the letter "K" to the right,
        # so it doesn't touch the y-axis
        if K < rel_x_pos * 2:
            annotations[1][0] = K + rel_x_pos

        # If "K" is relatively close to "K + C", the annotation 'jumps' to the other side, so that they don't
        # intersect with eachother 
        if (K + modelled_price - K) < rel_x_pos * 3:
            annotations[2][0] = K + modelled_price + rel_x_pos * 1.5

    # Put option 
    else:
        annotations = [
            [-rel_x_pos, -modelled_price, "-P"],
            [K + rel_x_pos, rel_y_pos, "K"],
            [K - modelled_price + rel_x_pos * 1.5, rel_y_pos, "K - P"]
        ]   

        # If "K" is relatively close to "K + P", the annotation 'jumps' to the other side, so that they don't
        # intersect with eachother - this time for the put option, so it's the other way
        if (K + modelled_price - K) < rel_x_pos * 3:
            annotations[2][0] = K - modelled_price - rel_x_pos * 1.5

    return annotations

def create_basic_option_graph(S, K, maximum_stock_value, maximum_strike_value, modelled_price, option_type):    

    fixed_input_max = max(maximum_stock_value, maximum_strike_value)
    variable_input_max = max(S, K)

    # x-axis 10-times the original size for the infinite profit possibility for Call options with S(t) -> +inf
    x_prices = np.linspace(
        0, fixed_input_max * 10, int(fixed_input_max * 20)
    )

    if option_type == "Call":  
        y_profit = np.maximum(x_prices - K, 0) - modelled_price
    else:
        y_profit = np.maximum(K - x_prices, 0) - modelled_price

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = x_prices,
        y = y_profit,
        mode = "lines"
    ))

    # Adding the main axes to the figure
    create_axes(fig)    

    # Dashed lines placement [x, y] (different for Call and Put options)
    dashed_lines = [
        [K, max(x_prices)],
        [K + (modelled_price if option_type == "Call" else -modelled_price), max(x_prices)]
    ]

    # Dashed lines graphing
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

    # Horizontal dashed line to connect the "-P" to the actual part of the function
    if option_type == "Put":
        fig.add_shape(
            type="line",
            x0=0,
            x1=K,
            y0=-modelled_price,
            y1=-modelled_price,
            line=dict(color="white", width=1, dash="dash"),
            xref="x",
            yref="y",
            opacity=0.1
        )

    # Names of axes and the size of the graph
    fig.update_layout(
        xaxis_title = "S(t)",
        yaxis_title = "Payoff (in €)",
        height = 500,
    )

    # The final graph will be "zoomed" on the important parts based on their size and location
    
    # This means that the positions of the annotations have to be changed relatively to the "zoom"

    x_axis_output_visual = [-(variable_input_max / 15), K + modelled_price + variable_input_max / 2.5]
    x_visual_span = x_axis_output_visual[1] - x_axis_output_visual[0]
    rel_x_pos = x_visual_span / 30

    y_axis_output_visual = [-modelled_price - variable_input_max / 15, modelled_price + variable_input_max / 15]
    y_visual_span = y_axis_output_visual[1] - y_axis_output_visual[0]
    rel_y_pos = y_visual_span / 30

    annotations = get_annotations(K, option_type, modelled_price, rel_x_pos, rel_y_pos)

    # Here we add the annotations to the graph using the positions defined earlier
    for x, y, label in annotations:
        fig.add_annotation(
            x = x,
            y = y,
            text = label,
            showarrow = False,
            font = dict(size = 14)
        )

    # x and y axes are adjusted accordingly to the size and shape of the graph
    fig.update_xaxes(range = x_axis_output_visual)
    fig.update_yaxes(range = y_axis_output_visual)

    return(fig)