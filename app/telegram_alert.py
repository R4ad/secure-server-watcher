from dataclasses import dataclass

import requests

from app.config import settings
from app.logger import get_logger


logger = get_logger()


@dataclass(frozen=True)
class TelegramResult:
    success: bool
    status_code: int | None
    message: str


def is_telegram_configured() -> bool:
    return bool(settings.telegram_bot_token and settings.telegram_chat_id)


def send_telegram_message(text: str) -> TelegramResult:
    if not is_telegram_configured():
        logger.warning("Telegram alert skipped because configuration is missing")
        return TelegramResult(
            success=False,
            status_code=None,
            message="Telegram configuration is missing",
        )

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            logger.info("Telegram alert sent successfully")
            return TelegramResult(
                success=True,
                status_code=response.status_code,
                message="Telegram alert sent successfully",
            )

        safe_error_message = (
            f"Telegram alert failed with status code {response.status_code}"
        )

        logger.error(safe_error_message)

        return TelegramResult(
            success=False,
            status_code=response.status_code,
            message=safe_error_message,
        )

    except requests.Timeout:
        safe_error_message = "Telegram request timed out"

        logger.error(safe_error_message)

        return TelegramResult(
            success=False,
            status_code=None,
            message=safe_error_message,
        )

    except requests.ConnectionError:
        safe_error_message = "Telegram connection failed"

        logger.error(safe_error_message)

        return TelegramResult(
            success=False,
            status_code=None,
            message=safe_error_message,
        )

    except requests.RequestException as exc:
        safe_error_message = f"Telegram request failed: {type(exc).__name__}"

        logger.error(safe_error_message)

        return TelegramResult(
            success=False,
            status_code=None,
            message=safe_error_message,
        )
