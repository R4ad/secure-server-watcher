import argparse
import time

from app.alert_cooldown import (
    get_remaining_cooldown_seconds,
    mark_alert_as_sent,
    should_send_alert,
)
from app.config import settings
from app.logger import get_logger
from app.port_checker import PortAlert, check_unexpected_open_ports, get_listening_ports
from app.service_checker import ServiceAlert, ServiceStatus, check_services
from app.system_monitor import (
    ResourceAlert,
    check_resource_thresholds,
    format_uptime,
    get_current_time,
    get_system_metrics,
)
from app.telegram_alert import send_telegram_message
from app.ssh_monitor import SSHAlert, SSHAnalysis, check_ssh_activity


logger = get_logger()


def build_system_report() -> tuple[str, list[ResourceAlert]]:
    metrics = get_system_metrics()

    report = (
        "Secure Server Watcher\n"
        "---------------------\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        f"CPU Usage: {metrics.cpu_usage}%\n"
        f"RAM Usage: {metrics.ram_usage}%\n"
        f"Disk Usage: {metrics.disk_usage}%\n"
        f"Uptime: {format_uptime(metrics.uptime_seconds)}"
    )

    alerts = check_resource_thresholds(
        metrics=metrics,
        cpu_threshold=settings.cpu_threshold,
        ram_threshold=settings.ram_threshold,
        disk_threshold=settings.disk_threshold,
    )

    return report, alerts


def build_resource_alert_message(alert: ResourceAlert) -> str:
    return (
        "⚠️ Secure Server Watcher Alert\n\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        f"Alert: {alert.title}\n"
        f"Metric: {alert.metric_name}\n"
        f"Current Value: {alert.current_value:.1f}{alert.unit}\n"
        f"Threshold: {alert.threshold}{alert.unit}"
    )


def build_port_alert_message(alert: PortAlert) -> str:
    process_text = "Unknown"

    if alert.process_name:
        process_text = alert.process_name

        if alert.pid is not None:
            process_text += f" ({alert.pid})"

    return (
        "⚠️ Suspicious Open Port Detected\n\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        f"Port: {alert.port}\n"
        f"Address: {alert.address}\n"
        f"Process: {process_text}\n"
        f"Allowed Ports: {', '.join(str(port) for port in alert.allowed_ports)}"
    )


def build_service_alert_message(alert: ServiceAlert) -> str:
    error_text = ""

    if alert.error:
        error_text = f"\nError: {alert.error}"

    return (
        "🚨 Critical Service Down\n\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        f"Service: {alert.service_name}\n"
        f"Status: {alert.status}"
        f"{error_text}"
    )


def send_test_telegram_alert() -> None:
    message = (
        "✅ Secure Server Watcher Test Alert\n\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        "Telegram alert system is working."
    )

    result = send_telegram_message(message)

    if result.success:
        print("Telegram test alert sent successfully.")
    else:
        print("Telegram test alert failed.")
        print(f"Reason: {result.message}")


def handle_resource_alert(alert: ResourceAlert) -> None:
    print(f"- {alert.message}")
    logger.warning(alert.message)

    if not should_send_alert(alert.key):
        remaining_seconds = get_remaining_cooldown_seconds(alert.key)

        print(
            f"  Telegram skipped because cooldown is active "
            f"({remaining_seconds} seconds remaining)."
        )

        logger.info(
            "Alert skipped due to cooldown: %s, remaining seconds: %s",
            alert.key,
            remaining_seconds,
        )

        return

    telegram_message = build_resource_alert_message(alert)
    result = send_telegram_message(telegram_message)

    if result.success:
        mark_alert_as_sent(alert.key)
        logger.info("Alert marked as sent: %s", alert.key)
    else:
        logger.error(
            "Alert was not marked as sent because Telegram delivery failed: %s",
            alert.key,
        )


def handle_port_alert(alert: PortAlert) -> None:
    print(f"- {alert.message}")
    logger.warning(alert.message)

    if not should_send_alert(alert.key):
        remaining_seconds = get_remaining_cooldown_seconds(alert.key)

        print(
            f"  Telegram skipped because cooldown is active "
            f"({remaining_seconds} seconds remaining)."
        )

        logger.info(
            "Port alert skipped due to cooldown: %s, remaining seconds: %s",
            alert.key,
            remaining_seconds,
        )

        return

    telegram_message = build_port_alert_message(alert)
    result = send_telegram_message(telegram_message)

    if result.success:
        mark_alert_as_sent(alert.key)
        logger.info("Port alert marked as sent: %s", alert.key)
    else:
        logger.error(
            "Port alert was not marked as sent because Telegram delivery failed: %s",
            alert.key,
        )


def handle_service_alert(alert: ServiceAlert) -> None:
    print(f"- {alert.message}")
    logger.warning(alert.message)

    if not should_send_alert(alert.key):
        remaining_seconds = get_remaining_cooldown_seconds(alert.key)

        print(
            f"  Telegram skipped because cooldown is active "
            f"({remaining_seconds} seconds remaining)."
        )

        logger.info(
            "Service alert skipped due to cooldown: %s, remaining seconds: %s",
            alert.key,
            remaining_seconds,
        )

        return

    telegram_message = build_service_alert_message(alert)
    result = send_telegram_message(telegram_message)

    if result.success:
        mark_alert_as_sent(alert.key)
        logger.info("Service alert marked as sent: %s", alert.key)
    else:
        logger.error(
            "Service alert was not marked as sent because Telegram delivery failed: %s",
            alert.key,
        )


def print_open_ports() -> None:
    open_ports = get_listening_ports()

    print("Listening Ports")
    print("---------------")

    if not open_ports:
        print("No listening ports detected.")
        return

    for item in open_ports:
        process_text = item.process_name or "unknown"

        if item.pid is not None:
            process_text += f" ({item.pid})"

        print(f"- {item.port} | {item.address} | {process_text}")


def print_service_statuses(statuses: list[ServiceStatus]) -> None:
    print("Service Statuses")
    print("----------------")

    if not statuses:
        print("No services configured.")
        return

    for status in statuses:
        if not status.is_supported:
            print(f"- {status.service_name}: skipped ({status.error})")
            continue

        state = "OK" if status.is_active else "DOWN"
        print(f"- {status.service_name}: {state} ({status.status})")


def build_ssh_alert_message(alert: SSHAlert) -> str:
    top_ips_text = "\n".join(
        f"- {ip}: {count} failed attempts"
        for ip, count in alert.top_failed_ips
    )

    if not top_ips_text:
        top_ips_text = "- Unknown"

    return (
        "🚨 Suspicious SSH Activity\n\n"
        f"Server: {settings.server_name}\n"
        f"Time: {get_current_time()}\n\n"
        f"Failed Attempts: {alert.failed_attempts}\n"
        f"Threshold: {alert.threshold}\n"
        f"Log Path: {alert.log_path}\n\n"
        f"Top Failed IPs:\n{top_ips_text}"
    )


def handle_ssh_alert(alert: SSHAlert) -> None:
    print(f"- {alert.message}")
    logger.warning(alert.message)

    if not should_send_alert(alert.key):
        remaining_seconds = get_remaining_cooldown_seconds(alert.key)

        print(
            f"  Telegram skipped because cooldown is active "
            f"({remaining_seconds} seconds remaining)."
        )

        logger.info(
            "SSH alert skipped due to cooldown: %s, remaining seconds: %s",
            alert.key,
            remaining_seconds,
        )

        return

    telegram_message = build_ssh_alert_message(alert)
    result = send_telegram_message(telegram_message)

    if result.success:
        mark_alert_as_sent(alert.key)
        logger.info("SSH alert marked as sent: %s", alert.key)
    else:
        logger.error(
            "SSH alert was not marked as sent because Telegram delivery failed: %s",
            alert.key,
        )


def print_ssh_analysis(analysis: SSHAnalysis) -> None:
    print("SSH Status")
    print("----------")

    if not analysis.is_supported:
        print(f"SSH monitoring skipped: {analysis.error}")
        return

    print(f"Log Path: {analysis.log_path}")
    print(f"Failed Attempts: {analysis.total_failed_attempts}")

    if analysis.failed_ips:
        print("Top Failed IPs:")

        for ip, count in sorted(
            analysis.failed_ips.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]:
            print(f"- {ip}: {count}")
    else:
        print("Top Failed IPs: None")

    if analysis.successful_logins:
        print("Recent Successful Logins:")

        for login in analysis.successful_logins:
            print(f"- {login.username} from {login.ip} using {login.method}")
    else:
        print("Recent Successful Logins: None")


def run_single_check() -> None:
    report, resource_alerts = build_system_report()
    port_alerts = check_unexpected_open_ports(settings.allowed_ports)
    service_statuses, service_alerts = check_services(settings.services_to_check)
    ssh_analysis, ssh_alerts = check_ssh_activity(
        log_path=settings.ssh_log_path,
        failed_threshold=settings.ssh_failed_threshold,
    )

    print(report)
    print()

    if resource_alerts:
        print("Resource Alerts:")

        for alert in resource_alerts:
            handle_resource_alert(alert)
    else:
        print("Resource Status: OK")
        logger.info("System resource status is OK")

    print()

    if port_alerts:
        print("Port Alerts:")

        for alert in port_alerts:
            handle_port_alert(alert)
    else:
        print("Port Status: OK")
        logger.info("Open port status is OK")

    print()

    print_service_statuses(service_statuses)

    if service_alerts:
        print()
        print("Service Alerts:")

        for alert in service_alerts:
            handle_service_alert(alert)
    else:
        logger.info("Service status is OK or skipped on this platform")

    print()
    print_ssh_analysis(ssh_analysis)

    if ssh_alerts:
        print()
        print("SSH Alerts:")

        for alert in ssh_alerts:
            handle_ssh_alert(alert)
    else:
        logger.info("SSH status is OK or skipped")

    logger.info("System monitoring check completed")


def run_loop() -> None:
    print(
        f"Secure Server Watcher loop started. "
        f"Interval: {settings.check_interval_seconds} seconds"
    )

    logger.info(
        "Loop mode started with interval %s seconds",
        settings.check_interval_seconds,
    )

    try:
        while True:
            run_single_check()

            print()
            print(
                f"Next check in {settings.check_interval_seconds} seconds..."
            )
            print("-" * 50)

            time.sleep(settings.check_interval_seconds)

    except KeyboardInterrupt:
        print()
        print("Secure Server Watcher stopped by user.")
        logger.info("Loop mode stopped by user")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Secure Server Watcher"
    )

    parser.add_argument(
        "--test-telegram",
        action="store_true",
        help="Send a test Telegram alert",
    )

    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List currently listening ports",
    )

    parser.add_argument(
        "--list-services",
        action="store_true",
        help="List configured service statuses",
    )

    parser.add_argument(
        "--check-ssh",
        action="store_true",
        help="Analyze SSH authentication logs",
    )

    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously using CHECK_INTERVAL_SECONDS",
    )

    args = parser.parse_args()

    logger.info("Secure Server Watcher started")

    if args.test_telegram:
        send_test_telegram_alert()
        logger.info("Telegram test completed")
        return

    if args.list_ports:
        print_open_ports()
        logger.info("Listening ports listed")
        return

    if args.list_services:
        service_statuses, _ = check_services(settings.services_to_check)
        print_service_statuses(service_statuses)
        logger.info("Service statuses listed")
        return

    if args.check_ssh:
        ssh_analysis, ssh_alerts = check_ssh_activity(
            log_path=settings.ssh_log_path,
            failed_threshold=settings.ssh_failed_threshold,
        )

        print_ssh_analysis(ssh_analysis)

        if ssh_alerts:
            print()
            print("SSH Alerts:")

            for alert in ssh_alerts:
                handle_ssh_alert(alert)

        logger.info("SSH monitoring check completed")
        return

    if args.loop:
        run_loop()
        return

    run_single_check()


if __name__ == "__main__":
    main()
