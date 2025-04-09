import pandas as pd
import io
import plotly.graph_objects as go


def plot(csv_data: str):
    cleaned_csv_data = "\n".join(
        [line.strip().rstrip(",") for line in csv_data.strip().split("\n")]
    )

    # Load the cleaned data into a pandas DataFrame
    df = pd.read_csv(io.StringIO(cleaned_csv_data), header=None)
    df.columns = ["timestamp", "reading_x", "reading_y", "reading_z"]
    # Convert timestamp to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Create the figure
    fig = go.Figure()

    # Plot each reading against the timestamp
    for col, color in zip(
        ["reading_x", "reading_y", "reading_z"], ["red", "green", "blue"]
    ):
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[col],
                mode="lines",
                name=col,
                line=dict(color=color),
            )
        )

    # Update layout
    fig.update_layout(
        title="Magnetic Readings Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Reading Value",
        template="plotly_white",
        legend_title="Readings",
    )
    return fig
