import plotly.graph_objects as go
import numpy as np
from pricing.option_pricing import EuropeanOption
from plotting.utils_plotting import create_axes, dashed_line
from config import OptionType, VariableKey

def get_annotations(K, option_type, modelled_price, rel_x_pos, rel_y_pos):
    
    # Annotation points added to the graph, mainly the important points like "C", "K", and the profit differential "K+C"

    if option_type == OptionType.CALL.value:
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

def profit_loss_areas(K, modelled_price, option_type, fig, max_x, arbitrary_high_value, color_config):

    # Adds a colored representation of the option payoff

    # The arbitrary_high_value scales the areas to appear infinite-like - mainly because of the infinite possible
    # profits of the call option

    colors = color_config.PAYOFF_AREAS

    if option_type == OptionType.CALL.value:
        fig.add_shape(
            type="rect",
            x0=0,
            x1=K,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[0],
            opacity=0.075,
            layer="below"
        )

        fig.add_shape(
            type="rect",
            x0=K,
            x1=K+modelled_price,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[1],
            opacity=0.075,
            layer="below"
        )

        fig.add_shape(
            type="rect",
            x0=K+modelled_price,
            x1=max_x,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[2],
            opacity=0.075,
            layer="below"
        )
        
    else:
        fig.add_shape(
            type="rect",
            x0=0,
            x1=K-modelled_price,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[2],
            opacity=0.075,
            layer="below"
        )

        fig.add_shape(
            type="rect",
            x0=K-modelled_price,
            x1=K,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[1],
            opacity=0.075,
            layer="below"
        )

        fig.add_shape(
            type="rect",
            x0=K,
            x1=max_x,
            y0=-arbitrary_high_value,
            y1=arbitrary_high_value,
            fillcolor=colors[0],
            opacity=0.075,
            layer="below"
        )

def hover_tooltips(K, modelled_price, option_type, fig, annotations, config):

    x_hover = []
    y_hover = []

    for i in range(0, len(annotations)):
        x_hover.append(annotations[i][0])
        y_hover.append(annotations[i][1])

    fig.add_trace(go.Scatter(
        x=x_hover,
        y=y_hover,
        mode="markers",
        marker=dict(size=10, color="rgba(0,0,0,0)"),  # invisible
        hoverinfo="text",
        hovertext=[
            f"Option price: {modelled_price:.2f} {config.CURRENCY}",
            f"Strike price: {K:.2f} {config.CURRENCY}",
            f"Break-even: {K + modelled_price:.2f} {config.CURRENCY}" if option_type == OptionType.CALL.value
            else f"Break-even: {K - modelled_price:.2f} {config.CURRENCY}"
        ],
        showlegend=False
    ))

def plot_payoffs(selected_parameters, modelled_price, config, 
                 color_config, color_toggle = False, bs_function_toggle = False):    
    try:
        S = selected_parameters[VariableKey.S.value]
        K = selected_parameters[VariableKey.K.value]
        option_type = selected_parameters[VariableKey.OPTION_TYPE.value]
    except KeyError as error:
        raise ValueError(f"Missing variable in the list: {error}")  

    fixed_input_max = max(config.STREAMLIT_INPUT_CONFIGS[VariableKey.S.value].max, 
                          config.STREAMLIT_INPUT_CONFIGS[VariableKey.K.value].max
                          )
    variable_input_max = max(S, K)

    # x-axis 10-times the original size for the infinite profit possibility for Call options with S(t) -> +inf
    x_prices = np.linspace(0, fixed_input_max * 10, 5000 + int(fixed_input_max * 20))

    if option_type == OptionType.CALL.value:  
        y_profit = np.maximum(x_prices - K, 0) - modelled_price
    else:
        y_profit = np.maximum(K - x_prices, 0) - modelled_price

    fig = go.Figure()
    create_axes(fig)

    fig.add_trace(go.Scatter(
        x = x_prices,
        y = y_profit,
        mode = "lines",
        hoverinfo="skip",
        showlegend=False
    ))

    # Names of axes and the size of the graph
    fig.update_layout(
        margin=dict(t=50, b=50, l=0, r=0),
        xaxis_title = "S(T)",
        yaxis_title = "Profit / Loss (in €)",
        height = 500
    )

    # Dashed lines to represent the intercepts of the function with the axes

    dashed_line(fig, [K], [-max(x_prices), max(x_prices)])
    dashed_line(fig, [K + (modelled_price if option_type == OptionType.CALL.value else -modelled_price)], [-max(x_prices), max(x_prices)])

    if option_type == OptionType.PUT.value:
        dashed_line(fig, [0, K], [-modelled_price], opacity=0.1)

    # The final graph will be "zoomed" on the important parts based on their size and location
    
    # This means that the positions of the annotations have to be changed relatively to the "zoom"

    if option_type == OptionType.CALL.value:
        x_axis_output_visual = [-(variable_input_max / 15), K + modelled_price + variable_input_max / 2.5]
    else:
        x_axis_output_visual = [-(variable_input_max / 15), K + variable_input_max / 2.5]
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

    hover_tooltips(K, modelled_price, option_type, fig, annotations, config)

    if color_toggle:
        profit_loss_areas(K, modelled_price, option_type, fig, max(x_prices), max(x_prices), color_config)

    # x and y axes are adjusted accordingly to the size and shape of the graph
    fig.update_xaxes(range = x_axis_output_visual)
    fig.update_yaxes(range = y_axis_output_visual)

    if bs_function_toggle:
        selected_parameters = selected_parameters.copy()
        selected_parameters[VariableKey.S.value] = x_prices
        black_scholes_values = EuropeanOption(**selected_parameters).bs_price()

        fig.add_trace(go.Scatter(
            x = x_prices,
            y = black_scholes_values - modelled_price,
            mode = "lines",
            hoverinfo="skip",
            showlegend=False
        ))

    return fig

def create_greek_graph(input_parameters, selected_variable, greek_to_plot, config, color_config):
    input_parameters = input_parameters.copy()
    x_values = np.linspace(config.STREAMLIT_INPUT_CONFIGS[selected_variable].min, 
                           config.STREAMLIT_INPUT_CONFIGS[selected_variable].max, 5000
                           )
    current_value = input_parameters[selected_variable]
    input_parameters[selected_variable] = x_values
    y_values = EuropeanOption(**input_parameters).bs_greeks(greek_to_return=greek_to_plot)

    fig = go.Figure()
    create_axes(fig)

    fig.add_trace(go.Scatter(
        x = x_values,
        y = y_values,
        mode = "lines",
        hoverinfo="skip",
        line=dict(color=color_config.SEAMLESS_GREY)
    ))

    fig.update_layout(
        xaxis_title = f"Variable {selected_variable}",
        height = 210,
        width = 200,
        title = f"Behaviour of {greek_to_plot}"
    )

    y_range = [min(y_values), max(y_values)]
    y_range_size_rel = (y_range[1] - y_range[0]) * 0.1
    fig.update_yaxes(range=[y_range[0] - y_range_size_rel, y_range[1] + y_range_size_rel])

    dashed_line(fig, [current_value], [-10, 10])

    fig.update_layout(margin=dict(t=30, b=20, l=0, r=0))

    return fig
