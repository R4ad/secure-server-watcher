from dataclasses import dataclass
from datetime import datetime
import time

import psutil


@dataclass(frozen=True)
class SystemMetrics:
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    uptime_seconds: int


@dataclass(frozen=True)
class ResourceAlert:
    key: str
    title: str
    metric_name: str
    current_value: float
    threshold: int
    unit: str = "%"

    @property
    def message(self) -> str:
        return (
            f"{self.title}: "
            f"{self.current_value:.1f}{self.unit} >= "
            f"{self.threshold}{self.unit}"
        )


def get_system_metrics() -> SystemMetrics:
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    return SystemMetrics(
        cpu_usage=cpu_usage,
        ram_usage=ram_usage,
        disk_usage=disk_usage,
        uptime_seconds=uptime_seconds,
    )


def format_uptime(uptime_seconds: int) -> str:
    days = uptime_seconds // 86400
    remaining = uptime_seconds % 86400

    hours = remaining // 3600
    remaining %= 3600

    minutes = remaining // 60

    parts: list[str] = []

    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    return ", ".join(parts)


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_resource_thresholds(
    metrics: SystemMetrics,
    cpu_threshold: int,
    ram_threshold: int,
    disk_threshold: int,
) -> list[ResourceAlert]:
    alerts: list[ResourceAlert] = []

    if metrics.cpu_usage >= cpu_threshold:
        alerts.append(
            ResourceAlert(
                key="resource_cpu_high",
                title="High CPU Usage",
                metric_name="CPU",
                current_value=metrics.cpu_usage,
                threshold=cpu_threshold,
            )
        )

    if metrics.ram_usage >= ram_threshold:
        alerts.append(
            ResourceAlert(
                key="resource_ram_high",
                title="High RAM Usage",
                metric_name="RAM",
                current_value=metrics.ram_usage,
                threshold=ram_threshold,
            )
        )

    if metrics.disk_usage >= disk_threshold:
        alerts.append(
            ResourceAlert(
                key="resource_disk_high",
                title="High Disk Usage",
                metric_name="Disk",
                current_value=metrics.disk_usage,
                threshold=disk_threshold,
            )
        )

    return alerts
