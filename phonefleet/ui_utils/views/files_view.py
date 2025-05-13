from nicegui import ui, run
from datetime import datetime


from phonefleet.ui_utils.aggrid import AgGrid
from phonefleet.ui_utils.context_managers import disable_buttons
from phonefleet.ui_utils.log_handler import logger
from phonefleet.ui_utils.views.plot_view import plot_view
from phonefleet.ui_utils.utils import plural


def files_table(files):
    return AgGrid(
        {
            "pagination": True,
            "paginationPageSize": 5,
            "paginationPageSizeSelector": [5, 10, 25, 50],
            "domLayout": "autoHeight",
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
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Device name",
                    "field": "device_name",
                    "filter": "agTextColumnFilter",
                    "floatingFilter": True,
                    "cellClass": "font-mono",
                    "filterParams": {
                        "applyMiniFilterWhileTyping": True,
                    },
                },
                {
                    "headerName": "Device IP",
                    "field": "device_ip",
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
                    "cellClass": "text-sm font-semibold uppercase",
                    "cellClassRules": {
                        # accelerometer
                        "text-green-600": 'data.sensor === "accelerometer"',
                        # gyroscope
                        "text-blue-600": 'data.sensor === "gyroscope"',
                        # magnetic field
                        "text-purple-600": 'data.sensor === "magnetic_field"',
                        # gps
                        "text-red-600": 'data.sensor === "gps"',
                    },
                },
            ],
            "rowSelection": {
                "mode": "multiRow",
                "headerCheckbox": True,
                "selectAllMode": "filtered",
                "enableClickSelection": True,
            },
            "defaultColDef": {
                "flex": 1,
                "wrapText": True,
                "autoHeight": True,
            },
        }
    ).classes("w-full h-full")


@ui.refreshable
def files_view(files, fleet):
    with ui.column().classes("w-full space-y-4"):
        files_grid = files_table(files)  # print selected file

        async def filter_files_by_sensor(sensor):
            logger.debug(f"Filtering files by sensor: {sensor}")
            await files_grid.run_grid_method(
                "setColumnFilterModel",
                "sensor",
                {
                    "filter": sensor,
                    "filterType": "text",
                    "type": "equals",
                },
            )
            await files_grid.run_grid_method("onFilterChanged")

        async def filter_files_today():
            today = datetime.now().strftime("%Y-%m-%d")
            logger.debug(f"Filtering files for today: {today}")
            await files_grid.run_grid_method(
                "setColumnFilterModel",
                "date",
                {
                    "dateFrom": today,
                    "dateTo": None,
                    "filterType": "date",
                    "type": "equals",
                },
            )
            await files_grid.run_grid_method("onFilterChanged")

        # only display the filter buttons if there are files
        with ui.row().bind_visibility_from(
            files_grid.options, "rowData", lambda x: len(x) > 0
        ):
            ui.button(
                "Filter today",
                on_click=filter_files_today,
                icon="today",
                color="indigo-300",
            )
            ui.button(
                "Accelerometer",
                on_click=lambda: filter_files_by_sensor("accelerometer"),
                icon="speed",
                color="green-300",
            )
            ui.button(
                "Gyroscope",
                on_click=lambda: filter_files_by_sensor("gyroscope"),
                icon="screen_rotation",
                color="blue-300",
            )
            ui.button(
                "Magnetic field",
                on_click=lambda: filter_files_by_sensor("magnetic_field"),
                icon="explore",
                color="purple-300",
            )
            ui.button(
                "GPS",
                on_click=lambda: filter_files_by_sensor("gps"),
                icon="location_on",
                color="red-300",
            )
            ui.button(
                "Reset filters",
                on_click=lambda: files_grid.run_grid_method("setFilterModel", None),
                icon="filter_alt_off",
                color="amber-400",
            )

        async def run_on_selected_files(func):
            rows = await files_grid.get_selected_rows()
            res = dict()
            if rows:
                for row in rows:
                    try:
                        ui.notify(f"Running on {row['filepath']}/{row['device_name']}")
                        v = await run.io_bound(func, row)
                        if v is not None:
                            res[f"{row['device_name']}_{row['filepath']}"] = v
                    except Exception as e:
                        logger.error(
                            f"Files: Error while running on {row['filepath']}/{row['device_name']}: {e}"
                        )
                        logger.exception(e)
            else:
                ui.notify("No device selected.")
            return res

        async def download_files():
            ui.notify("Downloading files...")

            def download_file(file_row):
                return fleet[file_row["device_ip"]].get_file(file_row["filepath"])

            res = await run_on_selected_files(download_file)
            total_files = sum(len(v) for v in res.values())
            logger.info(
                f"Downloaded {total_files} byte{plural(total_files)} from {len(res)} device{plural(res)}"
            )
            ui.notify(
                f"Downloaded {total_files} byte{plural(total_files)} from {len(res)} device{plural(res)}"
            )
            for k, v in res.items():
                ui.download(v.encode(), filename=k)

        async def plot_files():
            def plot_file(file_row):
                return (
                    fleet[file_row["device_ip"]],
                    fleet[file_row["device_ip"]].get_file(file_row["filepath"]),
                )

            plot_view.refresh(None, spinner=True)

            res = await run_on_selected_files(plot_file)
            if len(res) == 0:
                logger.error(res)
                ui.notify("No file selected.")
                return
            else:
                plot_view.refresh(res, spinner=False)
            total_files = sum(len(v) if v else 0 for _d, v in res.values())
            logger.info(
                f"Downloaded {total_files} bytes from {len(res)} device{plural(res)}"
            )
            ui.notify(
                f"Downloaded {total_files} bytes from {len(res)} device{plural(res)}"
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
