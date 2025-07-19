import numpy as np
import plotly.graph_objects as go
from config import MAX_GBM_LINES

def plot_gbm_paths(S_paths, S, T, r):
    n_paths, n_steps_plus1 = S_paths.shape
    steps = n_steps_plus1 - 1
    time_grid = np.linspace(0, T, steps + 1)

    fig = go.Figure()

    randomized_selection = np.random.choice(n_paths, min(MAX_GBM_LINES, n_paths), replace=False)

    non_risk_x = np.array([0, T])
    non_risk_linear_f = S * np.exp(r * non_risk_x)

    for i in randomized_selection:
        fig.add_trace(go.Scatter(
            x=time_grid,
            y=S_paths[i],
            mode="lines",
            name=f"Path {i+1}",
            line=dict(width=1),
            opacity=0.75
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
        showlegend=False,
        height=450
    )

    return fig