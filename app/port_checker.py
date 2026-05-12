from dataclasses import dataclass
import platform
import re
import subprocess

import psutil

from app.logger import get_logger


logger = get_logger()


@dataclass(frozen=True)
class OpenPort:
    port: int
    address: str
    pid: int | None
    process_name: str | None


@dataclass(frozen=True)
class PortAlert:
    key: str
    title: str
    port: int
    allowed_ports: list[int]
    address: str
    process_name: str | None = None
    pid: int | None = None

    @property
    def message(self) -> str:
        process_part = ""

        if self.process_name:
            process_part = f" | Process: {self.process_name}"

            if self.pid is not None:
                process_part += f" ({self.pid})"

        return (
            f"{self.title}: Port {self.port} is open "
            f"but not in allowed ports {self.allowed_ports}"
            f"{process_part}"
        )


def _get_process_name(pid: int | None) -> str | None:
    if pid is None:
        return None

    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def _extract_port_from_address(address_text: str) -> int | None:
    match = re.search(r":(\d+)(?:\s|$)", address_text)

    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


def _get_listening_ports_with_psutil() -> list[OpenPort]:
    listening_ports: dict[int, OpenPort] = {}

    connections = psutil.net_connections(kind="inet")

    for connection in connections:
        if connection.status != psutil.CONN_LISTEN:
            continue

        if not connection.laddr:
            continue

        try:
            port = connection.laddr.port
            address = connection.laddr.ip
        except AttributeError:
            address = str(connection.laddr[0])
            port = int(connection.laddr[1])

        process_name = _get_process_name(connection.pid)

        if port not in listening_ports:
            listening_ports[port] = OpenPort(
                port=port,
                address=address,
                pid=connection.pid,
                process_name=process_name,
            )

    return sorted(listening_ports.values(), key=lambda item: item.port)


def _get_listening_ports_with_lsof() -> list[OpenPort]:
    listening_ports: dict[int, OpenPort] = {}

    command = [
        "lsof",
        "-nP",
        "-iTCP",
        "-sTCP:LISTEN",
        "-F",
        "pcn",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        logger.warning("lsof command was not found.")
        return []

    if result.returncode != 0 and not result.stdout:
        logger.warning("lsof could not list listening ports: %s", result.stderr.strip())
        return []

    current_pid: int | None = None
    current_command: str | None = None

    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        field_type = line[0]
        field_value = line[1:]

        if field_type == "p":
            try:
                current_pid = int(field_value)
            except ValueError:
                current_pid = None

        elif field_type == "c":
            current_command = field_value

        elif field_type == "n":
            port = _extract_port_from_address(field_value)

            if port is None:
                continue

            if port not in listening_ports:
                listening_ports[port] = OpenPort(
                    port=port,
                    address=field_value,
                    pid=current_pid,
                    process_name=current_command,
                )

    return sorted(listening_ports.values(), key=lambda item: item.port)


def get_listening_ports() -> list[OpenPort]:
    try:
        return _get_listening_ports_with_psutil()

    except psutil.AccessDenied:
        logger.warning(
            "psutil could not access network connections. "
            "Trying lsof fallback."
        )

        if platform.system() == "Darwin":
            return _get_listening_ports_with_lsof()

        return []

    except OSError as exc:
        logger.warning("Could not list network connections with psutil: %s", exc)

        if platform.system() == "Darwin":
            return _get_listening_ports_with_lsof()

        return []


def check_unexpected_open_ports(allowed_ports: list[int]) -> list[PortAlert]:
    open_ports = get_listening_ports()
    alerts: list[PortAlert] = []

    allowed_ports_set = set(allowed_ports)

    for open_port in open_ports:
        if open_port.port not in allowed_ports_set:
            alerts.append(
                PortAlert(
                    key=f"port_unexpected_{open_port.port}",
                    title="Suspicious Open Port Detected",
                    port=open_port.port,
                    allowed_ports=allowed_ports,
                    address=open_port.address,
                    process_name=open_port.process_name,
                    pid=open_port.pid,
                )
            )

    return alerts
