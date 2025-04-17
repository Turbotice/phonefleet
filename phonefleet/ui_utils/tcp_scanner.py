import socket
import subprocess
import time
import logging
import re
import platform
from dataclasses import dataclass
from typing import List, Optional, Tuple
import ipaddress
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("network_scanner")


@dataclass
class NetworkDevice:
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    is_http_endpoint_available: bool = False
    endpoint_result: Optional[str] = None

    def __str__(self) -> str:
        return f"Device(ip={self.ip}, mac={self.mac}, hostname={self.hostname}, http_available={self.is_http_endpoint_available})"


class NetworkScanner:
    def __init__(
        self, scan_delay: float = 0.5, timeout: float = 1.0, target_port: int = 8080
    ):
        """Initialize the network scanner.

        Args:
            scan_delay: Delay between scanning hosts (in seconds) to avoid flooding
            timeout: Socket connection timeout (in seconds)
            target_port: The port to scan for (default: 8080)
        """
        self.scan_delay = scan_delay
        self.timeout = timeout
        self.target_port = target_port
        self.os_platform = platform.system().lower()
        self.scanning = False
        self.scan_progress = 0.0  # Progress indicator (0.0 to 1.0)
        self.n_discovered_devices = 0
        logger.debug(
            f"Initialized scanner on {self.os_platform} platform with delay={scan_delay}s, timeout={timeout}s"
        )

    def get_network_info(self) -> Tuple[str, str, int]:
        """Get local IP, subnet, and prefix length.

        Returns:
            Tuple containing (local_ip, network_address, prefix_length)
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connect to a public IP to determine which interface to use
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception as e:
            logger.error(f"Failed to determine local IP: {e}")
            # Fallback to localhost
            local_ip = "127.0.0.1"
        finally:
            s.close()

        # Always use /24 prefix as more reliable option
        # The detection logic was failing; using fixed prefix as requested
        prefix_length = 24

        # Create network address
        network_obj = ipaddress.IPv4Network(f"{local_ip}/{prefix_length}", strict=False)
        network_address = str(network_obj.network_address)

        logger.debug(
            f"Network info: local_ip={local_ip}, network={network_address}/{prefix_length}"
        )
        return local_ip, network_address, prefix_length

    def _subnet_mask_to_cidr(self, subnet_mask: str) -> int:
        """Convert subnet mask (e.g., 255.255.255.0) to CIDR prefix length."""
        mask_octets = subnet_mask.split(".")
        binary_str = ""
        for octet in mask_octets:
            binary_str += bin(int(octet))[2:].zfill(8)
        return binary_str.count("1")

    def _get_mac_address(self, ip: str) -> Optional[str]:
        """Get the MAC address for a given IP using ARP table."""
        mac = None

        # Platform-specific ARP table lookup
        try:
            if self.os_platform == "windows":
                output = subprocess.check_output(
                    f"arp -a {ip}", shell=True, universal_newlines=True
                )
                matches = re.search(
                    r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})",
                    output,
                )
                if matches:
                    mac = matches.group(0)
            elif self.os_platform == "darwin":  # macOS
                output = subprocess.check_output(
                    ["arp", "-n", ip], universal_newlines=True
                )
                matches = re.search(
                    r"([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})",
                    output,
                )
                if matches:
                    mac = matches.group(0)
            else:  # Linux and others
                output = subprocess.check_output(
                    ["arp", "-n", ip], universal_newlines=True
                )
                matches = re.search(
                    r"([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})",
                    output,
                )
                if matches:
                    mac = matches.group(0)
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.debug(f"Failed to get MAC address for {ip}: {e}")

        return mac

    def _get_hostname(self, ip: str) -> Optional[str]:
        """Try to resolve hostname from IP address."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror):
            return None

    def _check_endpoint(
        self, device: NetworkDevice, path: str = "status"
    ) -> Optional[str]:
        """Check if the device responds to HTTP requests on the target port and specified path."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((device.ip, self.target_port))

            # Simple HTTP GET request
            request = f"GET /{path} HTTP/1.1\r\nHost: {device.ip}:{self.target_port}\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode())

            # Set non-blocking mode
            s.setblocking(0)

            # Use select to implement timeout for receiving data
            import select

            readable, _, _ = select.select([s], [], [], self.timeout)

            if readable:
                # Socket is ready to read
                response = s.recv(1024)
                s.close()

                # If we got any response, consider the endpoint available
                # return len(response) > 0
                # check if we got a 200 response
                if response.startswith(b"HTTP/1.1 200"):
                    return response.decode(errors="ignore")
                else:
                    return None
            else:
                # Timeout occurred waiting for response
                logger.debug(
                    f"Timeout waiting for HTTP response from {device.ip}:{self.target_port}/{path}"
                )
                s.close()
                return None

        except (socket.timeout, socket.error, ConnectionRefusedError) as e:
            logger.debug(f"HTTP endpoint check failed for {device.ip}: {e}")
            return None

    def _scan_host(self, ip: str, tries: int = 1) -> Optional[NetworkDevice]:
        """Scan a single host for the target port."""
        for attempt in range(tries):
            try:
                # First do a quick check if the port is open
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.timeout)
                result = s.connect_ex((ip, self.target_port))
                s.close()

                if result == 0:  # Port is open
                    device = NetworkDevice(ip=ip)

                    # Get MAC address
                    device.mac = self._get_mac_address(ip)

                    # Try to get hostname
                    device.hostname = self._get_hostname(ip)

                    # Check specific HTTP endpoint with proper timeout handling
                    device.endpoint_result = self._check_endpoint(device)
                    device.is_http_endpoint_available = (
                        device.endpoint_result is not None
                    )

                    if device.is_http_endpoint_available:
                        logger.debug(
                            f"Device {ip} has port {self.target_port} open, endpoint available: {device.endpoint_result}"
                        )
                    else:
                        logger.debug(
                            f"Device {ip} has port {self.target_port} open, but endpoint is not available."
                        )

                    return device
            except Exception as e:
                logger.debug(f"Error scanning {ip}: {e}")
                return None
            time.sleep(self.scan_delay)
        return None

    def scan_network(
        self, start_offset: int = 0, max_hosts: int = 120, tries: int = 1
    ) -> List[NetworkDevice]:
        """Scan the network for devices with the target port open.

        Args:
            start_offset: Skip the first N IPs in the subnet
            max_hosts: Maximum number of hosts to scan

        Returns:
            List of NetworkDevice objects for devices with target port open
        """
        _, network_address, prefix_length = self.get_network_info()

        self.n_discovered_devices = 0
        self.scanning = True

        # Create network object and get list of hosts
        network = ipaddress.IPv4Network(f"{network_address}/{prefix_length}")

        # hosts = list(network.hosts())[start_offset: start_offset + max_hosts]

        # hosts to scan start at the xxx.xxx.xxx.start_offset address
        hosts = [
            ip for ip in network.hosts() if int(str(ip).split(".")[-1]) >= start_offset
        ]
        total_hosts = len(hosts)

        logger.info(
            f"Scanning {total_hosts} hosts (from offset {start_offset}, max {max_hosts})"
        )

        # Reset progress at the beginning of scan
        self.scan_progress = 0.0
        devices = []

        # Use ThreadPoolExecutor for parallel scanning
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(10, total_hosts)
        ) as executor:
            future_to_ip = {
                executor.submit(self._scan_host, str(ip), tries): str(ip)
                for ip in hosts
            }
            completed_count = 0

            for i, future in enumerate(concurrent.futures.as_completed(future_to_ip)):
                ip = future_to_ip[future]
                try:
                    device = future.result()
                    if device and device.is_http_endpoint_available:
                        devices.append(device)
                        self.n_discovered_devices += 1
                        if self.n_discovered_devices >= max_hosts:
                            logger.info(
                                f"Reached maximum number of hosts to scan: {max_hosts}"
                            )
                            # cancel remaining futures
                            for f in future_to_ip:
                                if f not in devices:
                                    f.cancel()
                            break
                        logger.debug(f"Found device: {device}")
                except Exception as e:
                    logger.error(f"Error processing {ip}: {e}")

                # Update progress
                completed_count += 1
                self.scan_progress = completed_count / total_hosts
                if completed_count % 20 == 0 or completed_count == total_hosts:
                    logger.info(
                        f"Scan progress: {self.scan_progress:.1%} ({completed_count}/{total_hosts})"
                    )

                # Apply scan delay but don't delay after the last item
                if i < total_hosts - 1:
                    time.sleep(self.scan_delay)

        # Ensure progress is set to 1.0 when complete
        self.scan_progress = 1.0
        logger.info(
            f"Scan complete. Found {len(devices)} devices with port {self.target_port} open"
        )

        self.scanning = False
        return devices


def scan_all_devices(
    scan_delay=0.5, timeout=1, start_offset=0, max_hosts=120
) -> List[NetworkDevice]:
    """Scan all devices on the network.

    Args:
        scan_delay: Delay between scanning hosts (in seconds)
        timeout: Socket connection timeout (in seconds)
        start_offset: Skip the first N IPs in the subnet
        max_hosts: Maximum number of hosts to scan

    Returns:
        List of NetworkDevice objects for devices with port 8080 open
    """
    logger.debug("Starting scan")
    # Scan and filter devices
    scanner = NetworkScanner(scan_delay=scan_delay, timeout=timeout)
    network_devices: List[NetworkDevice] = scanner.scan_network(
        start_offset=start_offset, max_hosts=max_hosts
    )
    logger.info(f"Scan progress at completion: {scanner.scan_progress:.2%}")
    return network_devices


if __name__ == "__main__":
    # Enable debug logging
    logger.setLevel(logging.DEBUG)

    # Example usage
    devices = scan_all_devices(scan_delay=0.2, timeout=1.0, max_hosts=50)

    print(f"Found {len(devices)} devices:")
    for device in devices:
        print(f"  {device}")

    # Filter for devices with HTTP endpoint available
    http_devices = [d for d in devices if d.is_http_endpoint_available]
    print(f"\nDevices with HTTP endpoint available: {len(http_devices)}")
    for device in http_devices:
        print(f"  {device}")
