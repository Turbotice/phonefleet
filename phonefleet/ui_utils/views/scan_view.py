from nicegui import ui, run
from phonefleet.device import Device
from phonefleet.ui_utils.views.devices_view import devices_view
from phonefleet.ui_utils.context_managers import disable_buttons
from phonefleet.ui_utils.tcp_scanner import NetworkScanner
from phonefleet.ui_utils.utils import plural
from phonefleet.ui_utils.log_handler import logger


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
