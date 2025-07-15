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

def dashed_line(fig, x_range, y_range, opacity = 1):

    if len(x_range) == 2 and len(y_range) == 1:
        fig.add_shape(
            type="line",
            x0=x_range[0],
            x1=x_range[1],
            y0=y_range[0],
            y1=y_range[0],
            line=dict(color="white", width=1, dash="dash"),
            opacity=opacity
        )
    elif len(x_range) == 1 and len(y_range) == 2:
        fig.add_shape(
            type="line",
            x0=x_range[0],
            x1=x_range[0],
            y0=y_range[0],
            y1=y_range[1],
            line=dict(color="white", width=1, dash="dash"),
            opacity=opacity
        )
    else:
        raise ValueError("Invalid x_range and y_range dimensions. Expected 2 for one axis and 1 for the other")