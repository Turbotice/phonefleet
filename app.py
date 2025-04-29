from datetime import datetime
import logging

from nicegui import ui, app


from phonefleet.ui_utils.fleet import fleet_to_files
from phonefleet.ui_utils.log_handler import logger, log_view
from phonefleet.ui_utils.views import devices_view
from phonefleet.ui_utils.views import scan_view
from phonefleet.ui_utils.views import plot_view
from phonefleet.ui_utils.views import files_view

# allow downloads
app.native.settings["ALLOW_DOWNLOADS"] = True

logger.setLevel(logging.DEBUG)

sample_fleet = {
    # f"192.168.0.{i}": Device(ip=f"192.168.0.{i}", mac=f"00:11:22:33:44:{i}")
    # for i in range(54, 170)
}

fleet_files = fleet_to_files(sample_fleet)


@ui.page("/")
def main_page():
    with ui.header():
        with ui.tabs().classes("w-full") as tabs:
            # ui.space()
            ui.tab("h", label="Devices", icon="smartphone")
            ui.tab("a", label="Files", icon="description")
            ui.tab("p", label="Plot", icon="insert_chart_outlined")
            # ui.button("Quit", on_click=app.shutdown, icon="close")
            ui.space()
            with ui.column().classes("self-end gap-0"):
                ui.label("PhoneFleet").classes("text-4xl font-bold self-end mb-px")
                ui.label("SUMMIT 2025").classes(
                    "text-[8pt] text-gray-200/30 italic mt-0 r-0 self-end"
                )
    with ui.tab_panels(tabs, value="h").classes("w-full"):
        with ui.tab_panel("h"):
            with ui.column().classes("w-full"):
                with ui.card(align_items="center").classes("w-full"):
                    with ui.row().classes("w-4/5 self-center"):
                        scan_view()
                    with ui.row().classes("w-full self-center h-80vh"):
                        devices_view(sample_fleet)
        with ui.tab_panel("a"):
            with ui.card(align_items="center").classes("w-full"):
                files_view(fleet_files, sample_fleet)
        with ui.tab_panel("p"):
            with ui.card(align_items="center").classes("w-full"):
                plot_view({})

    with ui.footer().classes("text-slate-900"):
        with ui.expansion("Log", icon="terminal", value=False).classes(
            "w-full absolute inset-x-0 bottom-0 bg-green-50"
        ):
            log_view()
    logger.info("App started at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Welcome to PhoneFleet!")


if __name__ in {"__main__", "__mp_main__"}:
    import sys

    args = sys.argv

    kwargs = {
        "show": "native" not in args,
        "title": "PhoneFleet",
        "reload": ("reload" in args),
        "reconnect_timeout": 5,
        "favicon": "📱",
    }
    if "native" in args:
        kwargs.update(
            {
                "fullscreen": ("fullscreen" in args),
                "native": True,
                "dark": False,
                "frameless": False,
                "window_size": (1300, 800),
            }
        )

    ui.run(
        **kwargs,
    )
