import json
import time
from pathlib import Path
from typing import Any

from app.config import settings
from app.logger import get_logger


logger = get_logger()

ALERT_STATE_FILE: Path = settings.log_file.parent / "alert_state.json"


def _load_alert_state() -> dict[str, Any]:
    if not ALERT_STATE_FILE.exists():
        return {}

    try:
        with ALERT_STATE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            logger.warning("Alert state file is invalid. Resetting state.")
            return {}

        return data

    except json.JSONDecodeError:
        logger.warning("Alert state file is corrupted. Resetting state.")
        return {}

    except OSError as exc:
        logger.error("Could not read alert state file: %s", exc)
        return {}


def _save_alert_state(state: dict[str, Any]) -> None:
    try:
        ALERT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with ALERT_STATE_FILE.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=2)

    except OSError as exc:
        logger.error("Could not save alert state file: %s", exc)


def should_send_alert(alert_key: str) -> bool:
    state = _load_alert_state()

    last_sent_at = state.get(alert_key)

    if last_sent_at is None:
        return True

    try:
        last_sent_at_float = float(last_sent_at)
    except (TypeError, ValueError):
        return True

    elapsed_seconds = time.time() - last_sent_at_float

    return elapsed_seconds >= settings.alert_cooldown_seconds


def mark_alert_as_sent(alert_key: str) -> None:
    state = _load_alert_state()
    state[alert_key] = time.time()
    _save_alert_state(state)


def get_remaining_cooldown_seconds(alert_key: str) -> int:
    state = _load_alert_state()

    last_sent_at = state.get(alert_key)

    if last_sent_at is None:
        return 0

    try:
        last_sent_at_float = float(last_sent_at)
    except (TypeError, ValueError):
        return 0

    elapsed_seconds = time.time() - last_sent_at_float
    remaining_seconds = settings.alert_cooldown_seconds - elapsed_seconds

    return max(0, int(remaining_seconds))
