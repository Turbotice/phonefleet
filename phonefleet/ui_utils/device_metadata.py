from dataclasses import dataclass
from phonefleet.ui_utils.defaults import DEFAULT_INVENTORY_FILE
from phonefleet.ui_utils.log_handler import logger


HEADER_TRANSLATION = {
    "#identification": "name",
    "Adresse MAC": "mac",
    "Mem": "mem",
    "Date mise en service": "register_date",
    "mdp": "password",
    "Etiqueté": "labeled",
    "Wi-Fi": "wifi",
    "ADB Debog +": "adb_debug",
    "Mode dev + adb WIFI": "adb_wifi",
    "PhyHack": "phyhack",
    "Gobannos": "gobannos",
    "Compte MI": "mi_account",
    "SIM": "sim",
    "Commentaire": "comment",
}


@dataclass
class DeviceMetadata:
    """
    A builder class for device metadata.
    The TABLE class variable is a dictionary that maps MAC addresses to device metadata.
    The init_table_from_file method initializes the TABLE variable from a CSV file.
    The from_mac method retrieves the metadata for a given MAC address.
    Example usage:
    # setup the DeviceMetadata class
    DeviceMetadata.init_table_from_file("path/to/your/csvfile.csv")
    # we can now retrieve metadata for a specific device
    metadata = DeviceMetadata.from_mac("00:11:22:33:44:55")
    print(metadata.name)
    """

    name: str
    mac: str
    mem: str
    register_date: str
    password: str
    labeled: str
    wifi: str
    adb_debug: str
    adb_wifi: str
    phyhack: str
    gobannos: str
    mi_account: str
    sim: str
    comment: str

    TABLE = {}

    @classmethod
    def from_mac(cls, mac: str) -> "DeviceMetadata":
        try:
            return cls(**cls.TABLE[mac])
        except KeyError:
            # raise KeyError(f"Device with MAC {mac} not found in metadata table.")
            logger.error(f"Device with MAC {mac} not found in metadata table.")
            return None

    def as_dict(self) -> dict[str, str]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}

    @classmethod
    def init_table_from_file(cls, csv_file: str):
        try:
            with open(csv_file, "r") as f:
                csv_data = f.read()
            cls.TABLE = cls.build_table(csv_data)
        except FileNotFoundError:
            logger.error(f"File {csv_file} not found. Metadata table will be empty.")
            cls.TABLE = {}

    @classmethod
    def build_table(cls, csv_data: str) -> dict[str, dict[str, str]]:
        lines = csv_data.split("\n")
        header = lines[0].split(";")
        header = [HEADER_TRANSLATION.get(h, h) for h in header]
        table = {}
        for line in lines[1:]:
            if not line:
                continue
            parts = line.split(";")
            # index by mac
            table[parts[1]] = {header[i]: parts[i] for i in range(len(header))}
        return table


DeviceMetadata.init_table_from_file(DEFAULT_INVENTORY_FILE)
