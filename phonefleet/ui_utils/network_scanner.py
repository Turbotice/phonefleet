import subprocess
import socket
import re
import platform
import uuid
import ipaddress
import time
from dataclasses import dataclass
from typing import List, Optional, Dict
from phonefleet.ui_utils.log_handler import logger
import netifaces


@dataclass
class NetworkDevice:
    hostname: str
    ip_address: str
    mac_address: str

    def __str__(self) -> str:
        return (
            f"Device: {self.hostname} | IP: {self.ip_address} | MAC: {self.mac_address}"
        )


class NetworkScanner:
    def __init__(self, scan_delay=0.1, timeout=1):
        """
        Initialize the network scanner

        Args:
            scan_delay (float): Delay in seconds between each ping request to avoid network overload
            timeout (int): Timeout in seconds for ping operations
        """
        self.local_devices = {}
        self.network_prefix = self._get_network_prefix()
        self.scan_delay = scan_delay
        self.timeout = timeout

    def _get_network_prefix(self) -> str:
        """Determine local network prefix based on default gateway interface"""
        gateways = netifaces.gateways()
        if "default" in gateways and netifaces.AF_INET in gateways["default"]:
            gateway_iface = gateways["default"][netifaces.AF_INET][1]
            addrs = netifaces.ifaddresses(gateway_iface)
            if netifaces.AF_INET in addrs:
                ip = addrs[netifaces.AF_INET][0]["addr"]
                netmask = addrs[netifaces.AF_INET][0]["netmask"]
                network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                return str(network)
        # Fallback to common home network
        return "192.168.1.0/24"

    def _get_local_info(self) -> NetworkDevice:
        """Get current machine's network information"""
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        mac_address = ":".join(
            [
                "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                for elements in range(0, 48, 8)
            ][::-1]
        )
        return NetworkDevice(hostname, ip_address, mac_address)

    def _get_arp_command(self):
        """Get the appropriate arp command based on the operating system"""
        system = platform.system()
        if system == "Windows":
            return ["arp", "-a"]
        elif system == "Darwin":  # macOS
            return ["arp", "-an"]
        else:  # Linux and others
            return ["arp", "-n"]

    def _parse_arp_output(self, arp_output: str) -> Dict[str, str]:
        """Parse ARP table output to extract IP-to-MAC mappings"""
        ip_to_mac = {}

        # Different parsing for different OS
        if platform.system() == "Windows":
            # Windows ARP output format
            pattern = (
                r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:]"
                + r"[0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2}[-:][0-9A-Fa-f]{2})"
            )
        else:
            # Unix/Linux/Mac ARP output format
            pattern = (
                r"\((\d+\.\d+\.\d+\.\d+)\).*?([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:"
                + r"[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})"
            )

        matches = re.findall(pattern, arp_output)
        for ip, mac in matches:
            ip_to_mac[ip] = mac.lower()

        return ip_to_mac

    def scan_network(self, start_offset=0, max_hosts=None) -> List[NetworkDevice]:
        """
        Scan the network and return a list of NetworkDevice objects

        Args:
            max_hosts (int, optional): Maximum number of hosts to scan, to limit network activity
                                     If None, will scan the entire subnet
        """
        # todo: maybe wipe the arp table first
        self.scanned_ips = set()

        devices = []

        # Add local machine first
        local_device = self._get_local_info()
        devices.append(local_device)
        self.local_devices[local_device.ip_address] = local_device

        # Run ping sweep to populate ARP cache
        network = ipaddress.IPv4Network(self.network_prefix)
        host_count = 0

        current_host = 0

        for ip in network.hosts():
            if current_host < start_offset - 1:
                current_host += 1
                continue
            ip_str = str(ip)
            if ip_str == local_device.ip_address:
                continue

            self.scanned_ips.add(ip_str)

            # Enforce max_hosts limit if specified
            host_count += 1
            if max_hosts is not None and host_count > max_hosts:
                break

            # Use ping command to populate ARP cache
            # if host_count % 10 == 0:
            #     print(f"Scanning host {host_count} ({ip_str})...")

            # Adjust ping command for macOS
            if platform.system() == "Darwin":  # macOS
                ping_cmd = ["ping", "-c", "1", "-t", str(self.timeout), ip_str]
            elif platform.system() == "Windows":
                ping_cmd = [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    str(int(self.timeout * 1000)),
                    ip_str,
                ]  # Windows uses milliseconds
            else:  # Linux and others
                ping_cmd = ["ping", "-c", "1", "-W", str(self.timeout), ip_str]

            try:
                logger.debug(f"Ping {ip_str}")
                subprocess.run(
                    ping_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=self.timeout + 1,
                )  # Add 1 second to timeout for process overhead
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

            # Add delay to avoid network congestion
            time.sleep(self.scan_delay)

        # Get ARP table with OS-specific command
        try:
            arp_cmd = self._get_arp_command()
            arp_output = subprocess.check_output(arp_cmd, universal_newlines=True)
            ip_to_mac = self._parse_arp_output(arp_output)

            # print(f"Found {len(ip_to_mac)} devices in ARP table")

            # Try to get hostnames and create device objects
            for ip, mac in ip_to_mac.items():
                try:
                    hostname = socket.getfqdn(ip)
                    # If hostname resolution returns just the IP, use a generic name
                    if hostname == ip:
                        hostname = f"unknown-device-{len(devices)}"
                except (socket.herror, socket.gaierror):
                    # If hostname resolution fails, use generic name
                    hostname = f"unknown-device-{len(devices)}"
                finally:
                    device = NetworkDevice(hostname, ip, mac)
                    devices.append(device)
                    self.local_devices[ip] = device

        except subprocess.SubprocessError as e:
            # print(f"Error retrieving ARP table: {e}")
            # print("Trying alternative method...")

            # On macOS, we can also try to read from the ARP cache file directly
            if platform.system() == "Darwin":
                try:
                    # Read from the ndp cache for IPv6 or arp cache for IPv4
                    arp_alternative = subprocess.check_output(
                        ["cat", "/var/db/arp_static"], universal_newlines=True
                    )
                    ip_to_mac = self._parse_alternate_arp(arp_alternative)

                    # Process any found devices
                    for ip, mac in ip_to_mac.items():
                        hostname = f"unknown-device-{len(devices)}"
                        device = NetworkDevice(hostname, ip, mac)
                        devices.append(device)
                        self.local_devices[ip] = device
                except subprocess.SubprocessError:
                    print("Alternative method also failed")

        return [d for d in devices if d.ip_address in self.scanned_ips]

    def _parse_alternate_arp(self, content: str) -> Dict[str, str]:
        """Parse alternate ARP sources for macOS"""
        ip_to_mac = {}
        # This is a simplified parser and might need adjustments based on actual format
        pattern = r"(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})"
        matches = re.findall(pattern, content)
        for ip, mac in matches:
            ip_to_mac[ip] = mac.lower()
        return ip_to_mac

    def get_device_by_ip(self, ip_address: str) -> Optional[NetworkDevice]:
        """Retrieve a device by its IP address"""
        return self.local_devices.get(ip_address)

    def get_device_by_hostname(self, hostname: str) -> Optional[NetworkDevice]:
        """Retrieve a device by its hostname"""
        for device in self.local_devices.values():
            if device.hostname.lower() == hostname.lower():
                return device
        return None

    def get_device_by_mac(self, mac_address: str) -> Optional[NetworkDevice]:
        """Retrieve a device by its MAC address"""
        mac_address = mac_address.lower()
        for device in self.local_devices.values():
            if device.mac_address.lower() == mac_address:
                return device
        return None


# Example usage
if __name__ == "__main__":
    scanner = NetworkScanner(scan_delay=0.1, timeout=1)

    # Scan network with a maximum of 10 hosts to prevent overloading large networks
    # Remove or adjust this parameter for different network sizes
    devices = scanner.scan_network(max_hosts=120)

    print(f"\nFound {len(devices)} devices on network {scanner.network_prefix}:")
    for device in devices:
        print(device)
