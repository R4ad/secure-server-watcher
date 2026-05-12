# Secure Server Watcher

A Python-based security and monitoring tool for Linux servers with Telegram alerts.

Secure Server Watcher helps monitor server health, SSH login activity, open ports, and critical services.  
It is designed for defensive security, personal infrastructure monitoring, and practical Linux security automation.

---

## Overview

Secure Server Watcher is a lightweight Python tool built to monitor Linux servers and send Telegram alerts when suspicious or unhealthy behavior is detected.

The project focuses on real-world defensive security tasks such as:

- Monitoring CPU, RAM, disk usage, and uptime
- Checking critical Linux services
- Detecting failed SSH login attempts
- Identifying suspicious IP addresses
- Checking open ports against an allowed list
- Sending Telegram alerts for important security or availability events
- Preventing repeated alert spam with cooldown logic

This project is built as a learning-focused and resume-ready security automation tool.

---

## Why This Project Exists

The goal of this project is not to build an offensive security tool.

The goal is to understand how real Linux servers behave, how logs can be analyzed, how basic security signals can be detected, and how automation can help respond faster to problems.

This project helps improve practical skills in:

- Python automation
- Linux server administration
- Defensive security monitoring
- SSH log analysis
- Service health checks
- Open port monitoring
- Telegram-based alerting
- Secure environment-based configuration
- Structured logging
- Basic alert cooldown design

---

## Features

### System Monitoring

Secure Server Watcher monitors basic server health metrics such as:

- CPU usage
- RAM usage
- Disk usage
- Server uptime

These checks help detect resource exhaustion before it causes downtime.

---

### SSH Security Monitoring

The tool analyzes SSH authentication activity and detects suspicious login behavior.

SSH monitoring features include:

- Failed SSH login attempt detection
- Top IP addresses with failed attempts
- Successful SSH login overview
- Basic brute-force detection logic
- Configurable failed-login threshold

Example use case:

If one IP address or multiple IP addresses cause many failed SSH login attempts, the tool can send a Telegram alert.

---

### Service Monitoring

The watcher checks whether important services are running.

Example services:

- SSH
- Nginx
- Docker

More services can be added through environment-based configuration.

Example:

```env
SERVICES_TO_CHECK=ssh,nginx,docker
```

If one of these services stops unexpectedly, the tool can send an alert.

---

### Open Port Checking

The tool checks listening ports and compares them against an allowed list.

Example allowed ports:

```env
ALLOWED_PORTS=22,80,443
```

If an unexpected port is open, the watcher can report it as suspicious.

Example:

```text
Allowed ports: 22, 80, 443
Detected ports: 22, 80, 443, 8080

Suspicious port detected: 8080
```

On macOS, the tool can use an `lsof` fallback when `psutil` cannot access network connections.

---

### Telegram Alerts

Secure Server Watcher sends Telegram notifications for important events.

Example alert types:

- High RAM usage
- High disk usage
- High CPU usage
- Too many failed SSH login attempts
- Critical service downtime
- Suspicious open ports

Example Telegram alert:

```text
⚠️ High RAM Usage

Server: my-server-1
RAM Usage: 91%
Threshold: 85%
Time: 2026-05-03 18:45
```

Telegram errors are logged safely without exposing the bot token.

---

### Alert Cooldown

The watcher includes cooldown logic to reduce repeated alert spam.

For example, if the same issue continues to exist, the tool can skip repeated Telegram alerts until the configured cooldown period expires.

```env
ALERT_COOLDOWN_SECONDS=1800
```

---

### Loop Mode

The watcher can run once or continuously.

Loop mode allows the tool to perform checks repeatedly using a configured interval.

```env
CHECK_INTERVAL_SECONDS=60
```

---

## Project Structure

```text
secure-server-watcher/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── system_monitor.py
│   ├── ssh_monitor.py
│   ├── port_checker.py
│   ├── service_checker.py
│   ├── telegram_alert.py
│   ├── alert_cooldown.py
│   └── logger.py
│
├── deployment/
│   └── secure-server-watcher.service.example
│
├── logs/
│   └── .gitkeep
│
├── sample_logs/
│   └── auth.log
│
├── .env.example
├── requirements.txt
├── README.md
├── .gitignore
└── run.sh
```

---

## Tech Stack

- Python
- psutil
- requests
- python-dotenv
- Linux system commands
- Telegram Bot API
- Logging
- Bash script runner

---

## Installation

Clone the repository:

```bash
git clone https://github.com/R4ad/secure-server-watcher.git
cd secure-server-watcher
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your own configuration.

Make the run script executable:

```bash
chmod +x run.sh
```

---

## Requirements

Add these dependencies to `requirements.txt`:

```txt
psutil
python-dotenv
requests
```

Install them with:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Example `.env.example` file:

```env
SERVER_NAME=my-server-1

TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

CPU_THRESHOLD=90
RAM_THRESHOLD=85
DISK_THRESHOLD=85

SSH_FAILED_THRESHOLD=10
SSH_LOG_PATH=/var/log/auth.log

ALLOWED_PORTS=22,80,443
SERVICES_TO_CHECK=ssh,nginx,docker

ALERT_COOLDOWN_SECONDS=1800
CHECK_INTERVAL_SECONDS=60
```

Never commit your real `.env` file to GitHub.

---

## Configuration Explanation

### SERVER_NAME

A human-readable name for the server.

Example:

```env
SERVER_NAME=vpn-server-1
```

This name appears in Telegram alerts.

---

### TELEGRAM_BOT_TOKEN

Telegram bot token used for sending alerts.

This value must be kept private and should never be committed to GitHub.

---

### TELEGRAM_CHAT_ID

The Telegram chat ID that receives alerts.

This can be your own Telegram user ID or a private admin group ID.

---

### CPU_THRESHOLD

The maximum allowed CPU usage percentage before an alert is triggered.

Example:

```env
CPU_THRESHOLD=90
```

---

### RAM_THRESHOLD

The maximum allowed RAM usage percentage before an alert is triggered.

Example:

```env
RAM_THRESHOLD=85
```

---

### DISK_THRESHOLD

The maximum allowed disk usage percentage before an alert is triggered.

Example:

```env
DISK_THRESHOLD=85
```

---

### SSH_FAILED_THRESHOLD

The number of failed SSH login attempts allowed before an alert is triggered.

Example:

```env
SSH_FAILED_THRESHOLD=10
```

---

### SSH_LOG_PATH

The path to the SSH authentication log file.

On Ubuntu/Debian servers, this is usually:

```env
SSH_LOG_PATH=/var/log/auth.log
```

For local development on macOS, a sample log file can be used:

```env
SSH_LOG_PATH=sample_logs/auth.log
```

---

### ALLOWED_PORTS

A comma-separated list of ports that are expected to be open.

Example:

```env
ALLOWED_PORTS=22,80,443
```

Any detected listening port outside this list can trigger a suspicious port alert.

---

### SERVICES_TO_CHECK

A comma-separated list of important services that should be running.

Example:

```env
SERVICES_TO_CHECK=ssh,nginx,docker
```

On Linux, these services are checked with `systemctl`.

---

### ALERT_COOLDOWN_SECONDS

The minimum time between repeated alerts for the same issue.

Example:

```env
ALERT_COOLDOWN_SECONDS=1800
```

This helps prevent alert spam.

---

### CHECK_INTERVAL_SECONDS

The interval between checks when running in loop mode.

Example:

```env
CHECK_INTERVAL_SECONDS=60
```

---

## Usage

Secure Server Watcher can be executed using the `run.sh` script.

Before running the tool, make sure the script is executable:

```bash
chmod +x run.sh
```

---

### Run a Single Monitoring Check

Run the watcher once and perform all available checks:

```bash
./run.sh
```

This command checks:

- System resources
- Open ports
- Configured services
- SSH authentication logs
- Telegram alert conditions

---

### Run in Loop Mode

Run the watcher continuously using the interval defined in `.env`:

```bash
./run.sh --loop
```

The interval is controlled by:

```env
CHECK_INTERVAL_SECONDS=60
```

Example behavior:

```text
Run check
Wait 60 seconds
Run check again
Wait 60 seconds
...
```

To stop loop mode, press:

```text
Ctrl + C
```

---

### Send a Test Telegram Alert

Use this command to test whether Telegram alerts are working:

```bash
./run.sh --test-telegram
```

Expected output:

```text
Telegram test alert sent successfully.
```

If Telegram is unreachable or the configuration is incorrect, the tool will show a safe error message without exposing the bot token.

---

### List Open Ports

Show currently listening ports:

```bash
./run.sh --list-ports
```

Example output:

```text
Listening Ports
---------------
- 22 | 0.0.0.0:22 | sshd
- 80 | 0.0.0.0:80 | nginx
- 443 | 0.0.0.0:443 | nginx
```

The watcher compares detected ports with the allowed ports configured in `.env`:

```env
ALLOWED_PORTS=22,80,443
```

Unexpected open ports can trigger alerts.

---

### List Configured Services

Check the status of configured services:

```bash
./run.sh --list-services
```

Example output on Linux:

```text
Service Statuses
----------------
- ssh: OK (active)
- nginx: OK (active)
- docker: OK (active)
```

On macOS, service checks are skipped because `systemctl` is only available on Linux:

```text
Service Statuses
----------------
- ssh: skipped (Service checking with systemctl is only supported on Linux.)
- nginx: skipped (Service checking with systemctl is only supported on Linux.)
- docker: skipped (Service checking with systemctl is only supported on Linux.)
```

Configured services are defined in `.env`:

```env
SERVICES_TO_CHECK=ssh,nginx,docker
```

---

### Analyze SSH Logs

Analyze SSH authentication logs:

```bash
./run.sh --check-ssh
```

Example output:

```text
SSH Status
----------
Log Path: /var/log/auth.log
Failed Attempts: 4

Top Failed IPs:
- 203.0.113.10: 3
- 198.51.100.55: 1

Recent Successful Logins:
- radman from 192.0.2.20 using publickey
```

If the number of failed SSH attempts reaches the configured threshold, the watcher can send a Telegram alert.

The SSH configuration is controlled by:

```env
SSH_LOG_PATH=/var/log/auth.log
SSH_FAILED_THRESHOLD=10
```

For local development on macOS, a sample log file can be used:

```env
SSH_LOG_PATH=sample_logs/auth.log
SSH_FAILED_THRESHOLD=3
```

---

### Common Commands

```bash
./run.sh
./run.sh --loop
./run.sh --test-telegram
./run.sh --list-ports
./run.sh --list-services
./run.sh --check-ssh
```

---

## Notes for macOS Development

This project is designed for Linux servers, but it can be developed and tested on macOS.

On macOS:

- System resource monitoring works normally
- Telegram alerts work if Telegram API is reachable
- Port checking uses an `lsof` fallback when `psutil` cannot access network connections
- Service checks are skipped because `systemctl` is not available
- SSH log analysis can be tested using a sample log file

Example local development configuration:

```env
SSH_LOG_PATH=sample_logs/auth.log
SSH_FAILED_THRESHOLD=10
ALLOWED_PORTS=22,80,443,49169,57113
CHECK_INTERVAL_SECONDS=60
```

For real Linux servers, use stricter production values.

---

## Notes for Linux Server Deployment

On a Linux server, the watcher can monitor real services, open ports, server resources, and SSH authentication logs.

Recommended production-style configuration:

```env
SERVER_NAME=vpn-server-1

CPU_THRESHOLD=90
RAM_THRESHOLD=85
DISK_THRESHOLD=85

SSH_LOG_PATH=/var/log/auth.log
SSH_FAILED_THRESHOLD=10

ALLOWED_PORTS=22,80,443
SERVICES_TO_CHECK=ssh,nginx,docker

ALERT_COOLDOWN_SECONDS=1800
CHECK_INTERVAL_SECONDS=60
```

Depending on your server setup, you may need permission to read SSH authentication logs.

On Ubuntu/Debian, SSH logs are usually stored at:

```text
/var/log/auth.log
```

The watcher should only be used on servers you own or are authorized to monitor.

---

## Example Alerts

### High RAM Usage

```text
⚠️ Secure Server Watcher Alert

Server: my-server-1
Time: 2026-05-03 18:45

Alert: High RAM Usage
Metric: RAM
Current Value: 91.0%
Threshold: 85%
```

---

### Critical Service Down

```text
🚨 Critical Service Down

Server: my-server-1
Time: 2026-05-03 18:45

Service: nginx
Status: inactive
```

---

### Suspicious SSH Activity

```text
🚨 Suspicious SSH Activity

Server: my-server-1
Time: 2026-05-03 18:45

Failed Attempts: 27
Threshold: 10

Top Failed IPs:
- 203.0.113.10: 18 failed attempts
- 198.51.100.55: 9 failed attempts
```

---

### Suspicious Open Port

```text
⚠️ Suspicious Open Port Detected

Server: my-server-1
Time: 2026-05-03 18:45

Port: 8080
Address: 0.0.0.0:8080
Process: unknown
Allowed Ports: 22, 80, 443
```

---

## Development Roadmap

- [x] Create initial project structure
- [x] Add system resource monitoring
- [x] Add Telegram alert integration
- [x] Add structured logging
- [x] Add service status checks
- [x] Add SSH log analysis
- [x] Add open port detection
- [x] Add alert cooldown system
- [x] Add loop mode
- [x] Add run script
- [ ] Add Linux deployment guide
- [ ] Add systemd service support
- [ ] Add Docker support
- [ ] Add FastAPI web dashboard

---

## Security Scope

This tool is intended only for:

- Your own servers
- Your own test environments
- Defensive monitoring
- Educational Linux security practice

This project should not be used to scan, monitor, or interact with systems without permission.

---

## What This Project Covers

Secure Server Watcher helps detect or monitor:

- Server resource exhaustion
- Disk space issues
- Service downtime
- Suspicious SSH login attempts
- Unexpected open ports
- Basic signs of brute-force activity
- Repeated alert conditions with cooldown handling

---

## What This Project Does Not Do

This tool does not:

- Exploit vulnerabilities
- Attack servers
- Bypass authentication
- Scan third-party systems
- Replace a full SIEM or EDR system
- Replace professional incident response

It is a lightweight defensive monitoring tool.

---

## Runtime Files

The following files are generated during execution and should not be committed to GitHub:

```text
logs/watcher.log
logs/alert_state.json
.env
```

Use `.gitignore` to keep sensitive and runtime files out of the repository.

---

## Future Improvements

Potential future features:

- JSON-based alert history
- SQLite event storage
- Web dashboard with FastAPI
- Dockerized deployment
- Multi-server monitoring
- Better SSH log parsing
- GeoIP lookup for suspicious IPs
- Integration with firewall rules
- Email alerts
- Discord alerts
- Prometheus metrics export

---

## Resume Summary

**Secure Server Watcher – Python Security Automation Tool**

Developed a Python-based Linux server monitoring tool with Telegram alerts.  
Implemented system resource monitoring, SSH log analysis, service health checks, open port detection, environment-based configuration, alert cooldown logic, loop mode, and structured logging for defensive server security.

---

## Status

MVP under active development.

---

## License

This project is currently released for educational and personal defensive security use.
