import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from config import MAX_GBM_LINES
from general import dashed_line

def kernel_density_vertical(fig, S_paths, T, randomized_selection):
    terminal_prices = S_paths[randomized_selection, -1]
    
    kde = gaussian_kde(terminal_prices)
    y_vals = np.linspace(min(terminal_prices), max(terminal_prices), 500)
    density_vals = kde(y_vals)

    scaled_density = density_vals / max(density_vals)

    fig.add_trace(go.Scatter(
        x = T + scaled_density,
        y = y_vals,
        mode="lines",
        line=dict(color="#595A70")
    ))

    fig.update_xaxes(range = [T - max(scaled_density) * 0.1, T + max(scaled_density) * 1.1])


def plot_gbm_paths(S_paths, T, r, seed):

    np.random.seed(seed)

    n_paths, n_steps_plus1 = S_paths.shape
    n_steps = n_steps_plus1 - 1
    time_grid = np.linspace(0, T, n_steps + 1)

    fig = go.Figure()
    fig_end_points = go.Figure()

    randomized_selection = np.random.choice(n_paths, min(MAX_GBM_LINES, n_paths), replace=False)

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

    kernel_density_vertical(fig_end_points, S_paths, T, randomized_selection)

    dashed_line(fig_end_points, [T-10000, T+10000], [S_paths[0][0] * np.exp(T * r)])

    return fig, fig_end_points