from nicegui import ui
from phonefleet.ui_utils.plot import plot_subgraphs_dict
from phonefleet.ui_utils.log_handler import logger
from phonefleet.ui_utils.utils import plural


@ui.refreshable
def plot_view(file_plots: dict):
    # file_plots is a dict of {filename: csv_data}
    # invert the dictionary
    # file_plots = {v: k for k, v in file_plots.items()}

    def plot_this(_):
        plot_container.clear()
        with plot_container:
            ui.spinner()
        t_offset = file_plots[select["value"]][0].lag_stats["tlag"]
        if t_offset is None:
            logger.warning(f"t_offset is None for {select['value']}, using 0 instead")
            t_offset = 0
        else:
            t_offset = t_offset * 1e9
        figure = plot_subgraphs_dict(
            file_plots[select["value"]][1], filename=select["value"], t_offset=t_offset
        )
        plot_container.clear()
        with plot_container:
            ui.plotly(figure).classes("w-full h-full min-h-50vh")

    with ui.column().classes("w-full"):
        select = dict()
        options = list(file_plots.keys())
        ui.label(f"{len(options)} file{plural(options)} available").classes(
            "text-slate-900 text-lg font-bold mb-2"
        )
        default = options[0] if len(options) > 0 else None
        select = dict() if default is None else {"value": default}
        with ui.row():
            ui.label("Select file to plot").classes("text-2xl font-bold")
            ui.select(options, value=default).bind_value_to(select).on_value_change(
                plot_this
            )
    plot_container = ui.row().classes("w-full h-full min-h-50vh")
    if default is not None:
        plot_this(None)
