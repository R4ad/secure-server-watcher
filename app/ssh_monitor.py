from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
import re

from app.logger import get_logger


logger = get_logger()


IP_PATTERN = re.compile(
    r"from (?P<ip>(?:\d{1,3}\.){3}\d{1,3}|[a-fA-F0-9:]+)"
)

FAILED_USER_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from"
)

ACCEPTED_LOGIN_PATTERN = re.compile(
    r"Accepted (?P<method>\S+) for (?P<user>\S+) from "
    r"(?P<ip>(?:\d{1,3}\.){3}\d{1,3}|[a-fA-F0-9:]+)"
)


@dataclass(frozen=True)
class SSHLoginEvent:
    username: str
    ip: str
    method: str
    raw_line: str


@dataclass(frozen=True)
class SSHAnalysis:
    log_path: Path
    is_supported: bool
    total_failed_attempts: int
    failed_ips: dict[str, int]
    successful_logins: list[SSHLoginEvent]
    error: str | None = None


@dataclass(frozen=True)
class SSHAlert:
    key: str
    title: str
    failed_attempts: int
    threshold: int
    top_failed_ips: list[tuple[str, int]]
    log_path: Path

    @property
    def message(self) -> str:
        top_ips_text = ", ".join(
            f"{ip} ({count})" for ip, count in self.top_failed_ips
        )

        if not top_ips_text:
            top_ips_text = "Unknown"

        return (
            f"{self.title}: {self.failed_attempts} failed SSH attempts "
            f">= threshold {self.threshold}. Top IPs: {top_ips_text}"
        )


def _read_recent_lines(log_path: Path, max_lines: int = 5000) -> list[str]:
    with log_path.open("r", encoding="utf-8", errors="ignore") as file:
        return list(deque(file, maxlen=max_lines))


def _extract_ip(line: str) -> str | None:
    match = IP_PATTERN.search(line)

    if not match:
        return None

    return match.group("ip")


def _extract_failed_username(line: str) -> str | None:
    match = FAILED_USER_PATTERN.search(line)

    if not match:
        return None

    return match.group("user")


def _extract_successful_login(line: str) -> SSHLoginEvent | None:
    match = ACCEPTED_LOGIN_PATTERN.search(line)

    if not match:
        return None

    return SSHLoginEvent(
        username=match.group("user"),
        ip=match.group("ip"),
        method=match.group("method"),
        raw_line=line.strip(),
    )


def analyze_ssh_log(log_path: Path) -> SSHAnalysis:
    if not log_path.exists():
        return SSHAnalysis(
            log_path=log_path,
            is_supported=False,
            total_failed_attempts=0,
            failed_ips={},
            successful_logins=[],
            error=f"SSH log file not found: {log_path}",
        )

    try:
        lines = _read_recent_lines(log_path)

    except PermissionError:
        logger.error("Permission denied while reading SSH log: %s", log_path)

        return SSHAnalysis(
            log_path=log_path,
            is_supported=False,
            total_failed_attempts=0,
            failed_ips={},
            successful_logins=[],
            error=f"Permission denied while reading SSH log: {log_path}",
        )

    except OSError as exc:
        logger.error("Could not read SSH log %s: %s", log_path, exc)

        return SSHAnalysis(
            log_path=log_path,
            is_supported=False,
            total_failed_attempts=0,
            failed_ips={},
            successful_logins=[],
            error=str(exc),
        )

    failed_ip_counter: Counter[str] = Counter()
    successful_logins: list[SSHLoginEvent] = []

    for line in lines:
        if "Failed password" in line:
            ip = _extract_ip(line)

            if ip:
                failed_ip_counter[ip] += 1

            # فعلاً username را فقط برای توسعه بعدی استخراج می‌کنیم
            _extract_failed_username(line)

        elif "Accepted " in line:
            login_event = _extract_successful_login(line)

            if login_event:
                successful_logins.append(login_event)

    return SSHAnalysis(
        log_path=log_path,
        is_supported=True,
        total_failed_attempts=sum(failed_ip_counter.values()),
        failed_ips=dict(failed_ip_counter),
        successful_logins=successful_logins[-5:],
        error=None,
    )


def check_ssh_activity(
    log_path: Path,
    failed_threshold: int,
) -> tuple[SSHAnalysis, list[SSHAlert]]:
    analysis = analyze_ssh_log(log_path)
    alerts: list[SSHAlert] = []

    if not analysis.is_supported:
        logger.info("SSH monitoring skipped: %s", analysis.error)
        return analysis, alerts

    if analysis.total_failed_attempts >= failed_threshold:
        top_failed_ips = Counter(analysis.failed_ips).most_common(5)

        alerts.append(
            SSHAlert(
                key="ssh_failed_attempts_high",
                title="Suspicious SSH Activity",
                failed_attempts=analysis.total_failed_attempts,
                threshold=failed_threshold,
                top_failed_ips=top_failed_ips,
                log_path=log_path,
            )
        )

    return analysis, alerts
