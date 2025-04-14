from collections import defaultdict
from datetime import datetime
from typing import Optional, Dict, Union
import numpy as np
import time
import socket
import requests
from enum import Enum


from ui_utils.log_handler import logger
from ui_utils.utils import plural

# from ui_utils.network_scanner import NetworkDevice, NetworkScanner
from ui_utils.tcp_scanner import NetworkDevice, NetworkScanner
from ui_utils.device_metadata import DeviceMetadata


class Commands:
    START = "start"
    STATUS = "status"
    STOP = "stop"
    SYNC = "kick-sync"
    CLEAN = "clean-files"
    LIST = "list-files"
    GET = "get-file"


class DeviceStatus(Enum):
    RECORDING = "recording"
    STOPPED = "stopped"
    UDP_CALIB = "UDP calib"
    UDP_CALIB_FINISHED = "UDP calib finished"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, status: str) -> "DeviceStatus":
        status = status.replace(" ", "_")
        return cls[status.upper()]


class Device:
    GLOBAL_ID = 0
    TIMEOUT = 10

    def __init__(
        self, ip: str, mac: str, port: str = "8080", name: Optional[str] = None
    ):
        self.ip = ip
        self.port = port
        self.mac = mac
        self.metadata = DeviceMetadata.from_mac(mac)
        self.experiment = None
        # a dict of filepath to content
        self.files = defaultdict()
        self.last_sync = None

        self.id = Device.GLOBAL_ID
        Device.GLOBAL_ID += 1
        if name is None:
            self.name = f"Phone-{str(self.ip).split('.')[-1]}"
        else:
            self.name = name
        self.status = DeviceStatus.UNKNOWN
        # self.update_status()

    @classmethod
    def from_network_device(cls, network_device: NetworkDevice) -> "Device":
        instance = cls(
            ip=network_device.ip,
            mac=network_device.mac,
            name=network_device.hostname,
        )
        try:
            instance.status = DeviceStatus.from_string(
                network_device.endpoint_result.splitlines()[-1].strip()
            )
        except KeyError:
            instance.status = DeviceStatus.UNKNOWN
        return instance

    def __str__(self) -> str:
        # Return a string representation of the device
        return f"Device(name={self.name}, ip_address={self.ip}, port={self.port}, mac_address={self.mac})"

    def _query(self, command: str) -> str:
        logger.debug(f"Querying {self.name}/{self.ip} with command {command}")
        url = f"http://{self.ip}:{self.port}/{command}"
        try:
            response = requests.get(url, timeout=Device.TIMEOUT)
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while querying {self.name}/{self.ip}")
            return None
        logger.debug(
            f"Response from {self.name}/{self.ip}: {response.text[:100]}{'' if len(response.text) < 100 else '...'}"
        )
        return response.text

    def start(self, experiment_name: Optional[str] = None) -> str:
        # todo: url-safe experiment_name
        if experiment_name is None or experiment_name == "":
            res = self._query(Commands.START)
        else:
            res = self._query(f"{Commands.START}?name={experiment_name}")
        self.status = DeviceStatus.RECORDING
        return res

    def stop(self) -> str:
        res = self._query(Commands.STOP)
        self.status = DeviceStatus.STOPPED
        return res

    def update_status(self) -> str:
        try:
            response = self._query(Commands.STATUS)
        except Exception as e:
            logger.warning(f"Error while updating status of {self.name}: {e}")
            return None

        if response is None:
            self.status = DeviceStatus.UNKNOWN
        else:
            try:
                self.status = DeviceStatus.from_string(response.strip())
            except KeyError:
                # we received an answer but we cannot parse it into a known status
                logger.warning(
                    f"Received an answer from {self.ip} but cannot parse it to a status"
                )
                logger.warning(
                    f"This may be a non-Gobannos server listening on port {self.port}"
                )
                self.status = DeviceStatus.UNKNOWN
        return self.status.value

    # def sync(self) -> dict:
    #     return time_sync(self.id)

    def _clear_files_cache(self):
        logger.debug("Clearing files cache")
        self.files = defaultdict()

    def clean(self) -> str:
        self._clean()
        # Gobannos requires confirmation in the form of a second call
        return self._clean()

    def _clean(self) -> str:
        return self._query(Commands.CLEAN)

    def get_file_list(self, experiment_name: Optional[str] = None) -> list:
        r = self._query(Commands.LIST)
        if r is None:
            return None
        r = r.removeprefix("[").removesuffix("]")
        files = [f.strip() for f in r.split(",") if f.strip()]
        for f in files:
            if experiment_name is None or f.startswith(experiment_name):
                if f not in self.files:
                    # insert into the keys
                    self.files[f] = None

        return list(self.files.keys())

    def get_file(self, filename: str) -> str:
        if filename in self.files:
            if self.files[filename] is not None:
                return self.files[filename]
        res = self._query(f"{Commands.GET}/{filename}")
        # todo: handle cache gracefully
        if res is None:
            return None
        self.files[filename] = res
        return res

    def time_sync(self, n: int = 1000, timeout: float = 0.1) -> Dict:
        """
        Perform time synchronization with the device.

        Args:
            n: Number of synchronization packets to send
            timeout: Socket timeout in seconds

        Returns:
            Dictionary with time lag statistics or None if sync failed
        """
        logger.info(f"Starting time synchronization with {self.name} ({self.ip})")
        sync_data = self._time_sync(n=n, timeout=timeout)

        if sync_data is None:
            logger.warning(f"Time synchronization failed with {self.name}")
            return None

        lag_stats = self._get_lag_stats(sync_data)

        if lag_stats is None:
            logger.warning(f"Failed to calculate lag statistics for {self.name}")
            return None

        logger.info(
            f"Time sync with {self.name}: lag={lag_stats['tlag'] * 1000:.2f}ms, std={lag_stats['tstd'] * 1000:.2f}ms"
        )
        self.lag_stats = lag_stats
        self.last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return lag_stats

    def _time_sync(self, n: int = 1000, timeout: float = 0.1) -> Union[Dict, None]:
        """
        Internal method to perform UDP-based time synchronization with device.

        Args:
            n: Number of synchronization packets to send
            timeout: Socket timeout in seconds

        Returns:
            Raw synchronization data dictionary or None if failed
        """
        # Command bytes for UDP protocol
        do_nothing = 0
        do_nothing_command = do_nothing.to_bytes(4, "big", signed=False)
        respond = 1
        respond_command = respond.to_bytes(4, "big", signed=False)
        stop = 2
        stop_command = stop.to_bytes(4, "big", signed=False)

        # Create a single socket for both sending and receiving
        try:
            # Close any existing sockets first to release port 5001
            # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # try:
            #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            # except AttributeError:
            #     # SO_REUSEPORT not available on this system
            #     pass

            # Bind to wildcard address with port 5001
            try:
                # sock.bind(("0.0.0.0", 5001))  # Use 0.0.0.0 instead of "" for clarity
                sock.bind(("::", 5001))  # Use 0.0.0.0 instead of "" for clarity
            except Exception as e:
                logger.warning(f"Failed to bind socket: {e}")
                sock.close()
                return None
            sock.settimeout(timeout)

            # Initialize UDP synchronization on the device
            try:
                # First send the do_nothing command
                logger.debug(f"Sending do_nothing command to {self.ip}:5000")
                sock.sendto(do_nothing_command, (self.ip, 5000))

                # Then initialize the UDP sync via HTTP
                logger.debug(f"Initializing UDP sync with {self.name} via HTTP")
                response = requests.get(
                    f"http://{self.ip}:{self.port}/udp-sync", timeout=Device.TIMEOUT
                )
                logger.debug(
                    f"UDP sync initialization response: {response.status_code}"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize UDP sync with {self.name}: {e}")
                sock.close()
                return None
            time.sleep(2.0)

            # Prepare data structures
            Dt = {}
            duration = []
            for i in range(1, 4):
                Dt[i] = []

            t0 = time.time()
            c = 0  # Counter for lost packets

            # Perform synchronization measurements
            for i in range(n):
                t1 = time.time_ns()
                sock.sendto(respond_command, (self.ip, 5000))
                t2 = time.time_ns()

                try:
                    # Explicitly set buffer size to 8 bytes
                    t_phone_bytes, addr = sock.recvfrom(8)
                    # t_phone_bytes, addr = b"\x00" * 8, (self.ip, 5000)

                    # Verify the sender address matches our expected phone
                    if not addr[0].endswith(self.ip):
                        logger.warning(
                            f"Received response from unexpected address: {addr[0]}"
                        )
                        continue

                    t3 = time.time_ns()

                    # Validate response length
                    if len(t_phone_bytes) != 8:
                        logger.warning(
                            f"Received malformed response of length {len(t_phone_bytes)}"
                        )
                        continue

                    t_phone = int.from_bytes(t_phone_bytes, byteorder="big")

                    duration.append((t3 - t1) * 10 ** (-9))
                    Dt[1].append((t1 - t_phone) * 10 ** (-9))
                    Dt[2].append((t2 - t_phone) * 10 ** (-9))
                    Dt[3].append((t3 - t_phone) * 10 ** (-9))

                    # Log first successful response
                    if len(duration) == 1:
                        logger.info(f"First successful response from {self.name}!")

                except socket.timeout:
                    c += 1
                    # if c % 10 == 0:
                    logger.warning(
                        f"Timeout receiving from {self.name}: {c}/{i + 1} packets lost"
                    )
                    continue
                except Exception as e:
                    c += 1
                    logger.error(f"Error receiving data from {self.name}: {e}")
                    continue

                # Early exit if we have enough successful responses
                if len(duration) >= 100 and i >= n // 2:
                    logger.info(
                        f"Collected {len(duration)} valid samples, stopping early"
                    )
                    break

            # Stop synchronization
            sock.sendto(stop_command, (self.ip, 5000))
            tend = time.time()
            logger.info(
                f"Time sync with {self.name}: Duration: {np.round((tend - t0) * 1000, decimals=3)}ms, "
                f"Packets sent: {n}, lost: {c}, received: {len(duration)}"
            )

            # Close socket
            sock.close()

            if len(duration) == 0:
                logger.warning(f"No successful time measurements with {self.name}")
                return None

            # Convert lists to numpy arrays and return data
            Dt["time"] = t0
            Dt["duration"] = np.array(duration)
            for key in [1, 2, 3]:
                Dt[key] = np.array(Dt[key])

            return Dt

        except Exception as e:
            logger.error(f"Unexpected error in time sync: {str(e)}")
            # Make sure we close the socket even on error
            try:
                sock.close()
            except Exception as close_error:
                logger.error(f"Error closing socket: {close_error}")
                return None

    def _get_lag_stats(self, Dt: Dict) -> Union[Dict, None]:
        """
        Calculate time lag statistics from synchronization data.

        Args:
            Dt: Time synchronization data from _time_sync

        Returns:
            Dictionary with lag statistics
        """
        if Dt is None or len(Dt["duration"]) == 0:
            return None

        duration = Dt["duration"]
        t0 = Dt["time"]
        tmedian = np.median(duration)

        tmax = tmedian * 1.5  # Filter out outliers (measurements taking too long)
        logger.debug(
            f"Median duration of UDP request with {self.name}: {np.round(tmedian * 1000, decimals=3)}ms"
        )

        # Filter measurements based on duration
        indices = np.where(duration <= tmax)[0]

        if len(indices) == 0:
            logger.warning(f"No valid measurements for {self.name} after filtering")
            return None

        # Calculate time lag using first and third timestamps
        tlag1 = np.asarray(Dt[1])[indices]
        tlag3 = np.asarray(Dt[3])[indices]
        tlag = (tlag1 + tlag3) / 2
        lag_median = np.median(tlag)

        # Return comprehensive statistics
        return {
            "tlag": lag_median,
            "dtmedian": tmedian,
            "tmin": np.min(tlag),
            "tmax": np.max(tlag),
            "tstd": np.std(tlag),
            "n": len(duration),
            "n_filtered": len(indices),
            "t0": t0,
            "device_id": self.id,
            "device_name": self.name,
            "device_ip": self.ip,
        }


def scan_all_devices(
    scan_delay=0.5, timeout=1, start_offset=0, max_hosts=120
) -> list[Device]:
    logger.debug("Starting scan")
    # scan and filter devices
    scanner = NetworkScanner(scan_delay=scan_delay, timeout=timeout)
    network_devices = scanner.scan_network(
        start_offset=int(start_offset), max_hosts=int(max_hosts)
    )
    logger.debug("End scan")
    logger.debug(f"Found {len(network_devices)} live device{plural(network_devices)}")
    logger.debug(
        f"Network Device{plural(network_devices)}: {[network_device.ip_address for network_device in network_devices]}"
    )
    devices = [Device.from_network_device(d) for d in network_devices]
    logger.debug("Searching for Gobannos devices")

    for device in devices:
        device.update_status()

    filtered_devices = list(filter(lambda d: d.status != DeviceStatus.UNKNOWN, devices))
    logger.info(
        f"Found {len(filtered_devices)} live Gobannos device{plural(filtered_devices)}"
    )
    logger.info(
        f"Gobannos Device{plural(filtered_devices)}: {[d.ip for d in filtered_devices]}"
    )
    return filtered_devices


if __name__ == "__main__":
    import time

    device = Device("192.168.0.111", "00:11:22:33:44:55")
    print(device)
    print(device.update_status())
    print(device.clean())
    print(device.update_status())
    print(device.start("experiment1"))
    print(device.update_status())
    time.sleep(2)
    print(device.stop())
    print(device.update_status())
    # print(device.sync())
    print(device.get_file_list())
    print(device.get_file_list("experiment1"))
