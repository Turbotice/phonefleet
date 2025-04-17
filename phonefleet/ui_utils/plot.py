import pandas as pd
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from phonefleet.ui_utils.fleet import file_path_to_sensor


def plot(csv_data: str, filename: str) -> go.Figure:
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

    data_type = file_path_to_sensor(filename)

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
        title=f"{data_type.capitalize()} Readings Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Reading Value",
        template="plotly_white",
        legend_title="Readings",
    )
    return fig


def plot_subgraphs(csv_data: str, filename: str) -> go.Figure:
    # Clean the CSV data
    cleaned_csv_data = "\n".join(
        [line.strip().rstrip(",") for line in csv_data.strip().split("\n")]
    )

    # Load the cleaned data into a pandas DataFrame
    df = pd.read_csv(io.StringIO(cleaned_csv_data), header=None)
    df.columns = ["timestamp", "reading_x", "reading_y", "reading_z"]

    # Convert timestamp to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract data type from filename for the title
    data_type = file_path_to_sensor(filename)

    # Create a figure with 3 subplots (stacked vertically)
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,  # Share x-axes among all subplots
        vertical_spacing=0.1,  # Add some space between the plots
        subplot_titles=(
            f"{data_type.capitalize()} X Reading",
            f"{data_type.capitalize()} Y Reading",
            f"{data_type.capitalize()} Z Reading",
        ),
    )

    # Colors for each reading
    colors = ["red", "green", "blue"]

    # Add each reading as a separate subplot
    readings = ["reading_x", "reading_y", "reading_z"]

    for i, (reading, color) in enumerate(zip(readings, colors), 1):
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[reading],
                mode="lines",
                name=reading,
                line=dict(color=color),
            ),
            row=i,  # Place each trace in its own row
            col=1,
        )

    # Update layout
    fig.update_layout(
        title=f"{data_type.capitalize()} Readings Over Time",
        height=900,  # Increase height to accommodate three subplots
        template="plotly_white",
        showlegend=False,  # Hide legend as it's redundant with subplot titles
    )

    # Update y-axis titles for each subplot
    fig.update_yaxes(title_text="X Value", row=1, col=1)
    fig.update_yaxes(title_text="Y Value", row=2, col=1)
    fig.update_yaxes(title_text="Z Value", row=3, col=1)

    # Update x-axis title (only for the bottom subplot)
    fig.update_xaxes(title_text="Timestamp", row=3, col=1)

    return fig
