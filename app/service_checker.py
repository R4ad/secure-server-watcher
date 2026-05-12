from dataclasses import dataclass
import platform
import subprocess

from app.logger import get_logger


logger = get_logger()


@dataclass(frozen=True)
class ServiceStatus:
    service_name: str
    status: str
    is_active: bool
    is_supported: bool
    error: str | None = None


@dataclass(frozen=True)
class ServiceAlert:
    key: str
    title: str
    service_name: str
    status: str
    error: str | None = None

    @property
    def message(self) -> str:
        error_part = ""

        if self.error:
            error_part = f" | Error: {self.error}"

        return (
            f"{self.title}: Service '{self.service_name}' "
            f"is not active. Status: {self.status}"
            f"{error_part}"
        )


def is_service_check_supported() -> bool:
    return platform.system() == "Linux"


def check_service_status(service_name: str) -> ServiceStatus:
    if not is_service_check_supported():
        return ServiceStatus(
            service_name=service_name,
            status="unsupported",
            is_active=True,
            is_supported=False,
            error="Service checking with systemctl is only supported on Linux.",
        )

    command = ["systemctl", "is-active", service_name]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )

        status = result.stdout.strip() or result.stderr.strip() or "unknown"
        is_active = status == "active"

        return ServiceStatus(
            service_name=service_name,
            status=status,
            is_active=is_active,
            is_supported=True,
            error=None if is_active else result.stderr.strip() or None,
        )

    except FileNotFoundError:
        logger.error("systemctl command was not found.")

        return ServiceStatus(
            service_name=service_name,
            status="systemctl_not_found",
            is_active=False,
            is_supported=False,
            error="systemctl command was not found.",
        )

    except subprocess.TimeoutExpired:
        logger.error("Service check timed out for service: %s", service_name)

        return ServiceStatus(
            service_name=service_name,
            status="timeout",
            is_active=False,
            is_supported=True,
            error="systemctl command timed out.",
        )

    except OSError as exc:
        logger.error("Could not check service %s: %s", service_name, exc)

        return ServiceStatus(
            service_name=service_name,
            status="error",
            is_active=False,
            is_supported=True,
            error=str(exc),
        )


def check_services(service_names: list[str]) -> tuple[list[ServiceStatus], list[ServiceAlert]]:
    statuses: list[ServiceStatus] = []
    alerts: list[ServiceAlert] = []

    for service_name in service_names:
        status = check_service_status(service_name)
        statuses.append(status)

        if not status.is_supported:
            logger.info(
                "Service check skipped for %s because it is not supported on this platform.",
                service_name,
            )
            continue

        if not status.is_active:
            alerts.append(
                ServiceAlert(
                    key=f"service_down_{service_name}",
                    title="Critical Service Down",
                    service_name=service_name,
                    status=status.status,
                    error=status.error,
                )
            )

    return statuses, alerts
