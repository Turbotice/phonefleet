import pandas as pd
import io
import plotly.graph_objects as go

from phonefleet.ui_utils.fleet import file_path_to_sensor
from phonefleet.ui_utils.defaults import MAX_PLOT_POINTS


def plot_subgraphs_dict(csv_data: str, filename: str, t_offset=0) -> go.Figure:
    # Clean the CSV data
    # sample the data if sample is less than 1
    cleaned_csv_data = "\n".join(
        [line.strip().rstrip(",") for line in csv_data.strip().split("\n")]
    )

    # Load the cleaned data into a pandas DataFrame
    df = pd.read_csv(io.StringIO(cleaned_csv_data), header=None)
    # Drop lines with timestamp == -1
    df = df[df[0] != -1]
    # Apply time offset
    if t_offset != 0:
        df[0] = df[0] + t_offset

    if df.shape[0] > MAX_PLOT_POINTS:
        # Take a sample of the data
        sample = MAX_PLOT_POINTS / df.shape[0]
        df = df.sample(frac=sample, random_state=1)
    else:
        sample = 1.0

    if df.shape[1] == 4:
        df.columns = ["timestamp", "reading_x", "reading_y", "reading_z"]
    else:
        df.columns = ["timestamp"] + [f"reading_{i}" for i in range(1, df.shape[1])]

    # Convert timestamp to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="us")

    # sort the DataFrame by timestamp
    df = df.sort_values(by="timestamp")

    # Convert readings to numeric
    for i in range(1, df.shape[1]):
        df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors="coerce")

    # Extract data type from filename for the title
    data_type = file_path_to_sensor(filename)

    # Define colors and readings
    colors = ["red", "green", "blue"]
    if df.shape[1] == 4:
        readings = ["reading_x", "reading_y", "reading_z"]
    else:
        readings = [f"reading_{i}" for i in range(1, df.shape[1])]

    # Build data traces using the dict interface
    data_traces = []
    for i, (reading, color) in enumerate(zip(readings, colors), start=1):
        trace = {
            "type": "scatter",
            "mode": "lines",
            "x": df["timestamp"],
            "y": df[reading],
            "name": reading,
            "line": {"color": color},
            # assign each trace to its own axis
            "xaxis": f"x{i}",
            "yaxis": f"y{i}",
        }
        data_traces.append(trace)

    # Build layout with grid for subplots
    layout = {
        "title": {
            "text": f"{data_type.capitalize()} Readings Over Time ({sample:.2%} sample)"
        },
        "height": 900,
        "template": "plotly_white",
        "showlegend": False,
        # define a grid based on the number of readings
        "grid": {"rows": df.shape[1] - 1, "columns": 1, "pattern": "independent"},
    }
    timestamp_str = "Timestamp (with offset)" if t_offset != 0 else "Timestamp"
    if df.shape[1] == 4:
        layout["yaxis"] = {"title": "X Value"}
        layout["yaxis2"] = {"title": "Y Value"}
        layout["yaxis3"] = {"title": "Z Value"}
        layout["xaxis3"] = {"title": timestamp_str}
    else:
        for i in range(1, df.shape[1]):
            layout[f"yaxis{i}"] = {"title": f"Reading {i}"}
            layout[f"xaxis{i}"] = {"title": timestamp_str}
            # hide x-axis titles for top subplots
            if i < df.shape[1] - 1:
                layout[f"xaxis{i}"] = {"visible": False}

    # Combine into a figure dict
    fig_dict = {"data": data_traces, "layout": layout}

    # Create Figure
    fig = go.Figure(fig_dict)
    return fig
