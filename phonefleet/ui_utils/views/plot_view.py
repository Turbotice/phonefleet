from nicegui import ui
from phonefleet.ui_utils.plot import plot_subgraphs_dict
from phonefleet.ui_utils.log_handler import logger
from phonefleet.ui_utils.utils import plural

DROPDOWN_HINT = "---- Select a file ----"


@ui.refreshable
def plot_graph(filename=None, device=None, csv_data=None):
    if filename is None or device is None or csv_data is None:
        return
    plot_spinner_view.refresh(True)
    t_offset = device.lag_stats["tlag"]
    if t_offset is None:
        logger.warning(f"t_offset is None for {filename}, using 0 instead")
        t_offset = 0
    else:
        t_offset = t_offset * 1e9
    figure = plot_subgraphs_dict(csv_data, filename=filename, t_offset=t_offset)
    ui.plotly(figure).classes("w-full h-full min-h-50vh")
    plot_spinner_view.refresh(False)


@ui.refreshable
def plot_select_view(file_plots: dict):
    if file_plots is None or len(file_plots) == 0:
        ui.label("No files available").classes("text-slate-900 text-lg font-bold mb-2")
        return
    # file_plots: {filename: (device, csv_data)}

    def update_plot(value_change):
        if value_change.value == DROPDOWN_HINT:
            plot_graph.refresh(None, None, None)
            return
        filename = value_change.value
        device, csv_data = file_plots[filename]
        plot_graph.refresh(filename, device, csv_data)

    with ui.column().classes("w-full"):
        if file_plots.keys():
            options = [DROPDOWN_HINT] + list(file_plots.keys())
        else:
            options = []
        available_files = (
            len(options) if DROPDOWN_HINT not in options else len(options) - 1
        )
        ui.label(f"{available_files} file{plural(available_files)} available").classes(
            "text-slate-900 text-lg font-bold mb-2"
        )
        with ui.row():
            ui.label("Select file to plot").classes("text-2xl font-bold")
            ui.select(options, value=options[0] if options else None).on_value_change(
                update_plot
            )

@ui.refreshable
def plot_spinner_view(spinner=False):
    if spinner:
        ui.spinner().props("size=lg").classes("text-slate-900")

@ui.refreshable
def plot_view(file_plots: dict, spinner=False):
    # file_plots: {filename: (device, csv_data)}

    plot_select_view(file_plots)
    plot_spinner_view(spinner)
    plot_graph(None, None, None)
