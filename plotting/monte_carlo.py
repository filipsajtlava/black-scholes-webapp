import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from plotting.utils_plotting import dashed_line

def kernel_density_vertical(fig, S_paths, T, randomized_selection, color_config):
    terminal_prices = S_paths[randomized_selection, -1]
    
    kde = gaussian_kde(terminal_prices)
    y_vals = np.linspace(min(terminal_prices), max(terminal_prices), 500)
    density_vals = kde(y_vals)

    scaled_density = density_vals / max(density_vals)

    fig.add_trace(go.Scatter(
        x = T + scaled_density,
        y = y_vals,
        mode="lines",
        line=dict(color=color_config.SEAMLESS_GREY)
    ))

    fig.update_xaxes(range = [T - max(scaled_density) * 0.1, T + max(scaled_density) * 1.1])


def plot_gbm_paths(S_paths, T, r, seed, config, color_config):

    np.random.seed(seed)

    n_paths, n_steps_plus1 = S_paths.shape
    n_steps = n_steps_plus1 - 1
    time_grid = np.linspace(0, T, n_steps + 1)

    fig = go.Figure()
    fig_end_points = go.Figure()

    randomized_selection = np.random.choice(n_paths, min(config.MAX_GBM_LINES, n_paths), replace=False)

    non_risk_x = np.array([0, T])
    non_risk_linear_f = S_paths[0,0] * np.exp(r * non_risk_x)

    for i in randomized_selection:
        fig.add_trace(go.Scatter(
            x=time_grid,
            y=S_paths[i],
            mode="lines",
            name=f"Path {i+1}",
            line=dict(width=1),
            opacity=0.75
        ))
        fig_end_points.add_trace(go.Scatter(
            x=[time_grid[-1]],
            y=[S_paths[i, -1]],
            name=f"Path {i+1}",
            mode="markers+lines"
        ))

    fig.add_trace(go.Scatter(
        x=non_risk_x,
        y=non_risk_linear_f,
        mode="lines",
        line=dict(color="white",
                  dash="dash")
    ))

    fig.update_layout(
        margin=dict(t=50, b=50, l=0, r=0),
        xaxis_title="t",
        yaxis_title="S(t)",
        height=450,
        showlegend=False,
    )

    S_paths_chosen = S_paths[randomized_selection, :]
    rel_adjust = (np.max(S_paths_chosen) - np.min(S_paths_chosen)) / 10
    fig.update_yaxes(range = [np.min(S_paths_chosen) - rel_adjust, np.max(S_paths_chosen) + rel_adjust])
    fig_end_points.update_yaxes(range = [np.min(S_paths_chosen) - rel_adjust, np.max(S_paths_chosen) + rel_adjust])

    fig_end_points.update_xaxes(tickmode="array",
                                tickvals=[T],
                                ticktext=["T"])

    fig_end_points.update_layout(
        margin=dict(t=50, b=50, l=0, r=0),
        showlegend=False
    )

    kernel_density_vertical(fig_end_points, S_paths, T, randomized_selection, color_config)

    dashed_line(fig_end_points, [T-10000, T+10000], [S_paths[0][0] * np.exp(T * r)])

    return fig, fig_end_points

def plot_confidence_interval(modelled_price, confidence_interval, option_type, color_config):

    if modelled_price > 1:
        round_decimal = 2
    else:
        round_decimal = 4

    modelled_price = round(modelled_price, round_decimal)
    confidence_interval = [round(val, round_decimal) for val in confidence_interval]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=confidence_interval,
        y=[0, 0],
        mode="lines+markers",
        line=dict(color=color_config.SEAMLESS_GREY),
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[modelled_price],
        y=[0],
        mode="markers",
        hoverinfo="text",
        hovertext=f"{option_type} option price",
        line=dict(color=color_config.option_type_red_green(option_type))
    ))

    fig.update_layout(
        margin=dict(t=25, b=25, l=0, r=0),
        height=75,
        showlegend=False,
        title=f"95% confidence interval"
    )

    fig.update_yaxes(
        visible=False
    )

    x_axis_values = [confidence_interval[0], modelled_price, confidence_interval[1]]
    buffer = (max(x_axis_values) - min(x_axis_values)) * 0.15

    fig.update_xaxes(tickmode="array",
                     tickvals=x_axis_values,
                     range=[min(x_axis_values) - buffer, max(x_axis_values) + buffer]
                     )

    return fig