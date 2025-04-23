from datetime import datetime
from phonefleet.device import Device


def fleet_to_dict(fleet: dict[str, Device]) -> list[dict]:
    return [
        {
            "ip": d.ip,
            "mac": d.mac,
            "status": d.status.value,
            "last_sync": d.last_sync,
            "metadata": ", ".join(
                f"{key}: [{value}]" for key, value in d.metadata.as_dict().items()
            )
            if d.metadata
            else None,
        }
        for d in fleet.values()
    ]


def file_path_to_sensor(file_path: str) -> str:
    sensors = ["accelerometer", "gyroscope", "magnetic_field", "gps", "usb"]
    for sensor in sensors:
        if sensor in file_path:
            return sensor
    return "unknown"


def extract_experiment_name(file_path: str) -> str:
    if file_path.startswith("202"):
        return ""
    return file_path.split("-")[0]


def _extract_datetime(file_path: str) -> datetime:
    if not file_path.startswith("202"):
        file_path = file_path.split("-", maxsplit=1)[1]
        # parse date from filename
        # 2025-03-18T12_08_07-<other stuff>
    try:
        res = datetime.strptime(file_path[:19], "%Y-%m-%dT%H-%M-%S")
    except ValueError:
        res = datetime.strptime(file_path[:19], "%Y-%m-%dT%H_%M_%S")
    return res


def extract_date(file_path: str) -> str:
    dt = _extract_datetime(file_path)
    return dt.strftime("%Y-%m-%d")


def extract_time(file_path: str) -> str:
    dt = _extract_datetime(file_path)
    return dt.strftime("%H:%M:%S")


def fleet_to_files(fleet: dict[str, Device]) -> list[dict]:
    return [
        {
            "filepath": f,
            "device_ip": ip,
            "sensor": file_path_to_sensor(f),
            "experiment": extract_experiment_name(f),
            "date": extract_date(f),
            "time": extract_time(f),
        }
        for ip, device in fleet.items()
        for f in device.files
    ]
