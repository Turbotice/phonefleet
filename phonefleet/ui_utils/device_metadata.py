"""
#identification;Adresse MAC;Mem;Date mise en service;mdp;Etiqueté;Wi-Fi;ADB Debog +;Mode dev + adb WIFI;PhyHack;Gobannos;Compte MI;SIM;Commentaire
XRed10_0;94:7b:ae:48:62:74;128;15/10/23;_01012000;Oui;Oui;Oui;;Oui;Oui;Turbots;AE;
XRed10_1;e0:80:6b:1e:f8:aa;64;15/10/23;_01012000;Oui;Oui;Oui;Oui;Oui;Oui;Turbots;SP;
"""

from dataclasses import dataclass


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


def build_table(csv_data: str) -> dict[str, dict[str, str]]:
    lines = csv_data.split("\n")
    header = lines[0].split(";")
    header = [HEADER_TRANSLATION.get(h, h) for h in header]
    table = {}
    for line in lines[1:]:
        if not line:
            continue
        parts = line.split(";")
        table[parts[0]] = {header[i]: parts[i] for i in range(len(header))}
    return table


@dataclass
class DeviceMetadata:
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

    @classmethod
    def from_mac(cls, table: dict[str, dict[str, str]], mac: str) -> "DeviceMetadata":
        return cls(**table[mac])
