from nicegui import ui, run
import pandas as pd
from datetime import datetime

from phonefleet.device import Device, DeviceStatus
from phonefleet.ui_utils.aggrid import AgGrid
from phonefleet.ui_utils.context_managers import disable_buttons
from phonefleet.ui_utils.views.files_view import files_view
from phonefleet.ui_utils.fleet import fleet_to_dict, fleet_to_files
from phonefleet.ui_utils.log_handler import logger
from phonefleet.ui_utils.utils import plural


@ui.refreshable
def table(fleet):
    grid = AgGrid(
        {
            "pagination": True,
            "paginationPageSize": 5,
            "paginationPageSizeSelector": [5, 10, 25, 50],
            "domLayout": "autoHeight",
            "rowHeight": 40,
            "rowData": fleet_to_dict(fleet),
            ":getRowId": "(params) => params.data.ip",
            "tooltipInteraction": True,
            "tooltipHideDelay": 40000,
            "rowSelection": {
                "mode": "multiRow",
                "headerCheckbox": True,
                "selectAllMode": "filtered",
                "enableClickSelection": True,
            },
            "columnDefs": [
                {
                    "headerName": "Device name",
                    "field": "name",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "IP",
                    "field": "ip",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
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
                    "tooltipField": "metadata",
                    "cellClassRules": {
                        "underline decoration-4 decoration-sky-800": "data.metadata !== null"
                    },
                },
                {
                    "headerName": "Last sync",
                    "field": "last_sync",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                        "filterOptions": [
                            "equals",
                            "lessThan",
                            "greaterThan",
                            "inRange",
                        ],
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
                    # "cellClass": "inline-block px-3 py-1 rounded-full text-sm font-semibold uppercase text-white max-w-fit max-h-fit m-2",
                    "cellClass": "text-sm font-semibold uppercase text-white max-w-fit max-h-fit",
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
    ).classes("w-full h-full")
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
            res = dict()
            if rows:
                for row in rows:
                    device = fleet[row["ip"]]
                    try:
                        v = await run.io_bound(func, device)
                        if v is not None:
                            res[device.ip] = v
                    except Exception as e:
                        logger.error(
                            f"Devices: Error while running on {device.ip}: {e}"
                        )
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

    async def download_tsyncs():
        res = await run_on_selected_devices(lambda d: d.lag_stats)
        # build a csv file, via df
        # name,tlag,tmedian,tmin,tmax,tstd,n,t0

        df = pd.DataFrame.from_dict(res, orient="index")
        # only keep the columns we want
        df = df[["device_name", "tlag", "dtmedian", "tmin", "tmax", "tstd", "n", "t0"]]
        # convert to csv
        csv_data = df.to_csv(index=False)
        # download the csv file
        filename = f"tsyncs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        ui.download(
            csv_data.encode(),
            filename=filename,
        )

        logger.info(f"Downloaded tsyncs from {len(res)} device{plural(res)}: {res}")

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

    async def time_sync(n: int = 200, ipv6: bool = False):
        # set status on selected devices
        rows = await grid.get_selected_rows()
        for row in rows:
            grid.run_row_method(
                row["ip"], "setDataValue", "status", DeviceStatus.UDP_CALIB.value
            )
        res = await run_on_selected_devices(
            lambda d: d.time_sync(n=n, timeout=0.1, ipv6=ipv6)
        )
        logger.info(f"Time synced on {len(res)} device{plural(res)}: {res}")
        logger.debug("Updating status")
        for row in rows:
            res = await run.io_bound(lambda d: d.update_status(), fleet[row["ip"]])
            grid.run_row_method(row["ip"], "setDataValue", "status", res)
            grid.run_row_method(
                row["ip"], "setDataValue", "last_sync", fleet[row["ip"]].last_sync
            )

    async def get_files_list():
        res = await run_on_selected_devices(lambda d: d.get_file_list())
        res_count_dict = {k: len(v) for k, v in res.items()}
        trunc_res_str = str(res_count_dict)[:100] + (
            "..." if len(str(res_count_dict)) > 100 else ""
        )
        logger.info(
            f"Count of files fetched on {len(res)} device{plural(res)}: {trunc_res_str}"
        )
        ui.notify(
            f"Count of files fetched on {len(res)} device{plural(res)}: {trunc_res_str}"
        )
        fleet_files = fleet_to_files(fleet)
        files_view.refresh(fleet_files, fleet)

    with ui.row().classes("space-x-4 self-center w-full"):
        # ui.label("Experiment")
        ui.icon("science").classes("text-green-300 text-4xl")
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
    with ui.row().classes("space-x-4 self-center w-full"):
        # ui.label("Time sync")
        ui.icon("access_time").classes("text-blue-300 text-4xl")
        n_tries_input = ui.number(
            "Probes", value=20, min=1, max=1000, step=1, precision=0
        )
        # ipv6_input = ui.checkbox("IPv6", value=False)
        ui.button(
            "Time sync",
            # on_click=lambda: time_sync(n=n_tries_input.value, ipv6=ipv6_input.value),
            on_click=lambda: time_sync(n=n_tries_input.value, ipv6=False),
            icon="alarm",
        )
        ui.button(
            "Download tsyncs",
            on_click=download_tsyncs,
            color="blue-300",
            icon="download",
        )
    with ui.row().classes("space-x-4 self-center w-full"):
        # ui.label("Files")
        ui.icon("description").classes("text-teal-300 text-4xl")
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
