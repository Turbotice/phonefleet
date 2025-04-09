from datetime import datetime
from device import Device, DeviceStatus  # , scan_all_devices
import logging

from nicegui import ui, run

from ui_utils.aggrid import AgGrid
from ui_utils.tcp_scanner import NetworkScanner
from ui_utils.utils import plural
from ui_utils.fleet import fleet_to_dict, fleet_to_files
from ui_utils.plot import plot
from ui_utils.log_handler import logger, log_view
from ui_utils.buttons_enabler import disable_buttons


logger.setLevel(logging.DEBUG)


sample_fleet = {
    f"192.168.0.{i}": Device(ip=f"192.168.0.{i}", mac=f"00:11:22:33:44:{i}")
    for i in range(54, 170)
}


fleet_files = fleet_to_files(sample_fleet)


def files_table(files):
    # return ui.aggrid(
    return AgGrid(
        {
            "rowData": files,
            "columnDefs": [
                {
                    "headerName": "File",
                    "field": "filepath",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "wrapText": True,
                    "autoHeight": True,
                    "checkboxSelection": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Device",
                    "field": "device",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Date",
                    "field": "date",
                    "filter": "agDateColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Time",
                    "field": "time",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                        "filterOptions": [
                            "startsWith",
                            "greaterThanOrEqual",
                            "lessThanOrEqual",
                        ],
                    },
                },
                {
                    "headerName": "Experiment",
                    "field": "experiment",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Sensor",
                    "field": "sensor",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
            ],
            "rowSelection": "multiple",
            "defaultColDef": {
                "flex": 1,
                "wrapText": True,
                "autoHeight": True,
            },
        }
    ).classes("w-full")


@ui.refreshable
def plot_view(file_plots: dict):
    # invert the dictionary
    file_plots = {v: k for k, v in file_plots.items()}
    first_file = next(iter(file_plots.keys()), None)

    with ui.column().classes("w-full"):
        select = dict()
        ui.select(file_plots, label="Select file", value=first_file).bind_value_to(
            select
        )
        if select["value"]:
            with disable_buttons():
                figure = plot(select["value"])
                ui.plotly(figure)


@ui.refreshable
def files_view(files):
    with ui.column().classes("w-full space-y-4"):
        files_grid = files_table(files)  # print selected file

        async def run_on_selected_files(func):
            with disable_buttons():
                rows = await files_grid.get_selected_rows()
                res = dict()
                if rows:
                    for row in rows:
                        try:
                            v = await run.io_bound(func, row)
                            if v is not None:
                                res[row["filepath"]] = v
                        except Exception as e:
                            logger.error(
                                f"Error while running on {row['filepath']}/{row['device']}: {e}"
                            )
                else:
                    ui.notify("No device selected.")
                return res

        async def download_files():
            def download_file(device):
                return sample_fleet[device["device"]].get_file(device["filepath"])

            res = await run_on_selected_files(download_file)
            total_files = sum(len(v) for v in res.values())
            logger.info(
                f"Downloaded {total_files} byte{plural(total_files)} from {len(res)} device{plural(res)}"
            )
            for k, v in res.items():
                ui.download(v.encode(), filename=k)

        async def plot_files():
            def plot_file(device):
                return sample_fleet[device["device"]].get_file(device["filepath"])

            res = await run_on_selected_files(plot_file)
            if len(res) == 0:
                ui.notify("No file selected.")
                return
            if len(res) > 1:
                logger.warning("Plotting multiple files is not supported yet.")
            else:
                plot_view.refresh(res)
            total_files = sum(len(v) for v in res.values())
            logger.info(
                f"Downloaded {total_files} files from {len(res)} device{plural(res)}"
            )
            plot_view.refresh(res)

        with ui.row():
            ui.button(
                "Download", on_click=download_files, color="green-300", icon="get_app"
            )
            ui.button(
                "Plot",
                on_click=plot_files,
                color="blue-300",
                icon="insert_chart_outlined",
            )


@ui.refreshable
def table(fleet):
    # grid = ui.aggrid(
    grid = AgGrid(
        {
            "rowHeight": 50,
            "rowData": fleet_to_dict(fleet),
            ":getRowId": "(params) => params.data.ip",
            "rowSelection": {
                "mode": "multiRow",
                "headerCheckbox": True,
                "selectAllMode": "filtered",
                "enableClickSelection": True,
            },
            "columnDefs": [
                {
                    "headerName": "IP",
                    "field": "ip",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                    # "checkboxSelection": True,
                },
                {
                    "headerName": "MAC",
                    "field": "mac",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Status",
                    "field": "status",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                    "cellClass": "text-center uppercase rounded-md py-0.5 px-0.5 border max-h-8 max-w-24 m-2 border-transparent text-xs text-white transition-all shadow-sm",
                    "cellClassRules": {
                        # running
                        "bg-green-600": f'x === "{DeviceStatus.RECORDING.value}"',
                        # stopped
                        "bg-gray-400": f'x === "{DeviceStatus.STOPPED.value}"',
                        # calib in progress
                        "bg-blue-300": f'x === "{DeviceStatus.UDP_CALIB.value}"',
                        # calib finished
                        "bg-blue-500": f'x === "{DeviceStatus.UDP_CALIB_FINISHED.value}"',
                        # unknown
                        "bg-yellow-500": f'x === "{DeviceStatus.UNKNOWN.value}"',
                    },
                },
            ],
            "defaultColDef": {
                "flex": 1,
                "wrapText": True,
                "autoHeight": True,
            },
        }
    ).classes("w-full")
    return grid


@ui.refreshable
def devices_view(fleet: dict[str, Device]):
    grid = table(fleet)
    with ui.dialog() as clear_confirm_dialog, ui.card():
        with ui.row():
            ui.icon("warning").classes("text-red-500 text-4xl")
            ui.label("Are you sure you want to wipe the selected devices?")
        ui.label("This action is irreversible.")
        with ui.row():
            ui.button(
                "Yes, I am sure",
                on_click=lambda: clear_confirm_dialog.submit("Yes"),
                color="red-300",
                icon="delete",
            )
            ui.button(
                "No",
                on_click=lambda: clear_confirm_dialog.submit("No"),
                color="outline-primary",
            )

    async def run_on_selected_devices(func):
        with disable_buttons():
            rows = await grid.get_selected_rows()
            logger.debug(f"Selected rows: {rows}")
            res = dict()
            if rows:
                for row in rows:
                    device = fleet[row["ip"]]
                    try:
                        v = await run.io_bound(func, device)
                        if v is not None:
                            res[device.ip] = v
                    except Exception as e:
                        logger.error(f"Error while running on {device.ip}: {e}")
                        logger.exception(e)
            else:
                ui.notify("No device selected.")
            return res

    async def start_selected_devices(experiment_name: str):
        res = await run_on_selected_devices(lambda d: d.start(experiment_name))
        for ip in res.keys():
            grid.run_row_method(ip, "setDataValue", "status", fleet[ip].status.value)
        if experiment_name is None or experiment_name == "":
            logger.info(f"Started {len(res)} device{plural(res)}")
        else:
            logger.info(
                f"Started {len(res)} device{plural(res)} with experiment {experiment_name}"
            )

    async def stop_selected_devices():
        res = await run_on_selected_devices(lambda d: d.stop())
        for ip in res.keys():
            grid.run_row_method(ip, "setDataValue", "status", fleet[ip].status.value)
        logger.info(f"Stopped {len(res)} device{plural(res)}: {res}")

    async def clear_selected_devices():
        confirm = await clear_confirm_dialog
        if confirm == "Yes":
            res = await run_on_selected_devices(lambda d: d.clean())
            logger.info(f"Cleared {len(res)} device{plural(res)}: {res}")
        else:
            logger.info("Clear cancelled")

    async def update_status():
        res = await run_on_selected_devices(lambda d: d.update_status())
        for ip, status in res.items():
            grid.run_row_method(ip, "setDataValue", "status", status)
        logger.info(f"Status updated on {len(res)} device{plural(res)}: {res}")

    async def time_sync():
        # set status on selected devices
        rows = await grid.get_selected_rows()
        for row in rows:
            grid.run_row_method(
                row["ip"], "setDataValue", "status", DeviceStatus.UDP_CALIB.value
            )
        res = await run_on_selected_devices(lambda d: d.time_sync(n=200, timeout=0.1))
        logger.info(f"Time synced on {len(res)} device{plural(res)}: {res}")
        logger.debug("Updating status")
        for row in rows:
            res = await run.io_bound(lambda d: d.update_status(), fleet[row["ip"]])
            grid.run_row_method(row["ip"], "setDataValue", "status", res)

    async def get_files_list():
        res = await run_on_selected_devices(lambda d: d.get_file_list())
        res_count_dict = {k: len(v) for k, v in res.items()}
        trunc_res_str = str(res_count_dict)[:100] + (
            "..." if len(str(res_count_dict)) > 100 else ""
        )
        logger.info(
            f"Count of files fetched on {len(res)} device{plural(res)}: {trunc_res_str}"
        )
        fleet_files = fleet_to_files(fleet)
        files_view.refresh(fleet_files)

    with ui.row().classes("space-x-4 self-center"):
        experiment_name_input = ui.input("Experiment name")
        ui.button(
            "Start",
            on_click=lambda: start_selected_devices(experiment_name_input.value),
            color="green-300",
            icon="play_arrow",
        )
        ui.button(
            "Stop",
            on_click=stop_selected_devices,
            color="amber-400",
            icon="stop",
        )
        ui.button(
            "Update status",
            on_click=update_status,
            color="indigo-300",
            icon="refresh",
        )
        ui.button(
            "Clear",
            on_click=clear_selected_devices,
            color="red-300",
            icon="delete",
        )

        ui.button(
            "Get files list",
            on_click=get_files_list,
            color="teal-300",
            icon="folder",
        )
        ui.button(
            "Time sync",
            on_click=time_sync,
            icon="alarm",
        )


def scan_all_devices(
    scanner: NetworkScanner, start_offset=0, max_hosts=10, tries: int = 1
):
    devices = scanner.scan_network(
        start_offset=int(start_offset), max_hosts=int(max_hosts), tries=int(tries)
    )
    return [Device.from_network_device(d) for d in devices]


async def scan(scanner, start_offset=0, max_hosts=10, tries: int = 1):
    with disable_buttons():
        devices = await run.io_bound(
            scan_all_devices,
            scanner,
            start_offset=start_offset,
            max_hosts=max_hosts,
            tries=tries,
        )
        fleet = {d.ip: d for d in devices}
    logger.info(f"{len(fleet)} device{plural(fleet)} available")
    devices_view.refresh(fleet)


def scan_view():
    with ui.row().classes("w-full self-center justify-between"):
        offset_input = ui.number(
            "Start IP", value=100, precision=0, min=0, max=256, step=1
        )
        max_hosts_input = ui.number(
            "Max hosts", value=1, precision=0, min=1, max=256, step=1
        )
        scan_delay_input = ui.number(
            "Scan delay", value=0.05, precision=2, step=0.05, min=0.05, max=1
        )
        timeout_input = ui.number(
            "Timeout", value=1.0, precision=2, step=0.1, min=0.1, max=10
        )
        tries_input = ui.number("Tries", value=1, min=1, max=10, precision=0)
        scanner = NetworkScanner(
            scan_delay=scan_delay_input.value, timeout=timeout_input.value
        )
        ui.button(
            "Scan",
            on_click=lambda: scan(
                scanner,
                offset_input.value,
                max_hosts_input.value,
                tries_input.value,
            ),
            icon="wifi_tethering",
        )
    with ui.row().classes("w-full").bind_visibility_from(scanner, "scanning"):
        ui.linear_progress(show_value=False).bind_value_from(scanner, "scan_progress")
        with ui.row(align_items="stretch"):
            ui.label().bind_text_from(
                scanner, "scan_progress", backward=lambda x: f"{x:.1%}"
            )
            ui.space()
            ui.label().bind_text_from(
                scanner,
                "n_discovered_devices",
                backward=lambda x: f"{x} device{'s' if x > 1 else ''} discovered {'📱' * x}",
            )


@ui.page("/")
def main_page():
    with ui.header():
        with ui.tabs().classes("w-full") as tabs:
            # ui.space()
            ui.tab("h", label="Devices", icon="smartphone")
            ui.tab("a", label="Files", icon="description")
            ui.tab("p", label="Plot", icon="insert_chart_outlined")
            ui.space()
            with ui.column().classes("self-end gap-0"):
                ui.label("PhoneFleet").classes("text-4xl font-bold self-end mb-px")
                ui.label("SUMMIT 2025").classes(
                    "text-[8pt] text-gray-200/30 italic mt-0 r-0 self-end"
                )
    with ui.tab_panels(tabs, value="h").classes("w-full"):
        with ui.tab_panel("h"):
            with ui.card(align_items="center").classes("w-full"):
                with ui.row().classes("w-4/5 self-center"):
                    scan_view()
                with ui.row().classes("w-full h-full self-center"):
                    devices_view(sample_fleet)
        with ui.tab_panel("a"):
            with ui.card(align_items="center").classes("w-full"):
                files_view(fleet_files)
        with ui.tab_panel("p"):
            with ui.card(align_items="center").classes("w-full"):
                plot_view({})

    with ui.footer().classes("text-slate-900"):
        with ui.expansion("Log", icon="terminal", value=True).classes(
            "w-full absolute inset-x-0 bottom-0 bg-green-50"
        ):
            log_view()
    logger.info("App started at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("Welcome to PhoneFleet!")


if __name__ in {"__main__", "__mp_main__"}:
    import sys

    ui.run(reload=(sys.argv[-1] == "reload"))
