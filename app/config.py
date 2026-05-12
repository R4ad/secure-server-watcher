from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


def get_str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def get_int(key: str, default: int) -> int:
    value = os.getenv(key)

    if value is None or value.strip() == "":
        return default

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value for {key}: {value}")


def get_port_list(key: str, default: str = "") -> list[int]:
    value = os.getenv(key, default).strip()

    if not value:
        return []

    ports: list[int] = []

    for item in value.split(","):
        item = item.strip()

        if not item:
            continue

        try:
            ports.append(int(item))
        except ValueError:
            raise ValueError(f"Invalid port value in {key}: {item}")

    return ports


def get_str_list(key: str, default: str = "") -> list[str]:
    value = os.getenv(key, default).strip()

    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    server_name: str

    telegram_bot_token: str
    telegram_chat_id: str

    cpu_threshold: int
    ram_threshold: int
    disk_threshold: int

    ssh_failed_threshold: int

    allowed_ports: list[int]
    services_to_check: list[str]

    alert_cooldown_seconds: int
    check_interval_seconds: int

    log_file: Path


settings = Settings(
    server_name=get_str("SERVER_NAME", "unknown-server"),

    telegram_bot_token=get_str("TELEGRAM_BOT_TOKEN"),
    telegram_chat_id=get_str("TELEGRAM_CHAT_ID"),

    cpu_threshold=get_int("CPU_THRESHOLD", 90),
    ram_threshold=get_int("RAM_THRESHOLD", 85),
    disk_threshold=get_int("DISK_THRESHOLD", 85),

    ssh_failed_threshold=get_int("SSH_FAILED_THRESHOLD", 10),

    allowed_ports=get_port_list("ALLOWED_PORTS", "22,80,443"),
    services_to_check=get_str_list("SERVICES_TO_CHECK", "ssh,nginx,docker"),

    alert_cooldown_seconds=get_int("ALERT_COOLDOWN_SECONDS", 1800),
    check_interval_seconds=get_int("CHECK_INTERVAL_SECONDS", 60),

    log_file=BASE_DIR / "logs" / "watcher.log",
)
