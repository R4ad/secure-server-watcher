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

---

## Features

### System Monitoring

Secure Server Watcher can monitor basic server health metrics such as:

- CPU usage
- RAM usage
- Disk usage
- Server uptime

These checks help detect resource exhaustion before it causes downtime.

---

### SSH Security Monitoring

The tool is designed to analyze SSH authentication activity and detect suspicious login behavior.

Planned SSH monitoring features include:

- Failed SSH login attempt detection
- Top IP addresses with failed attempts
- Successful SSH login overview
- Basic brute-force detection logic

Example use case:

If one IP address fails SSH login many times in a short period, the tool can send a Telegram alert.

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

The tool can check listening ports and compare them against an allowed list.

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
│   └── logger.py
│
├── logs/
│   └── watcher.log
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

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/secure-server-watcher.git
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

ALLOWED_PORTS=22,80,443
SERVICES_TO_CHECK=ssh,nginx,docker

ALERT_COOLDOWN_SECONDS=1800
```

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

### ALLOWED_PORTS

A comma-separated list of ports that are expected to be open.

Example:

```env
ALLOWED_PORTS=22,80,443
```

---

### SERVICES_TO_CHECK

A comma-separated list of important services that should be running.

Example:

```env
SERVICES_TO_CHECK=ssh,nginx,docker
```

---

### ALERT_COOLDOWN_SECONDS

The minimum time between repeated alerts for the same issue.

Example:

```env
ALERT_COOLDOWN_SECONDS=1800
```

This helps prevent alert spam.

---

## Usage

Run the watcher manually:

```bash
python app/main.py
```

Expected example output:

```text
Server: my-server-1
CPU Usage: 14%
RAM Usage: 42%
Disk Usage: 68%
Uptime: 5 days, 3 hours
```

---

## Example Alerts

### High RAM Usage

```text
⚠️ High RAM Usage

Server: my-server-1
RAM Usage: 91%
Threshold: 85%
Time: 2026-05-03 18:45
```

### Critical Service Down

```text
🚨 Service Down

Server: my-server-1
Service: nginx
Status: inactive
Time: 2026-05-03 18:45
```

### Suspicious SSH Activity

```text
🚨 Suspicious SSH Activity

Server: my-server-1
Failed Login Attempts: 27
Top IP: 203.0.113.10
Time: 2026-05-03 18:45
```

### Suspicious Open Port

```text
⚠️ Suspicious Open Port Detected

Server: my-server-1
Port: 8080
Allowed Ports: 22, 80, 443
Time: 2026-05-03 18:45
```

---

## Development Roadmap

- [ ] Create initial project structure
- [ ] Add system resource monitoring
- [ ] Add Telegram alert integration
- [ ] Add structured logging
- [ ] Add service status checks
- [ ] Add SSH log analysis
- [ ] Add open port detection
- [ ] Add alert cooldown system
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
Implemented system resource monitoring, SSH log analysis, service health checks, open port detection, environment-based configuration, and structured logging for defensive server security.

---

## Status

Currently under development.

---

## License

This project is currently released for educational and personal defensive security use.
