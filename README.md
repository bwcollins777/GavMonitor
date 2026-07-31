# Nashville Fire Department Unit Monitor

A cloud-based Python application that monitors the Nashville Fire Department Active Incidents ArcGIS REST API every five minutes using GitHub Actions.

When a **new incident** includes **EN41** or **EN42** in the dispatched units, the application sends a formatted HTML email notification through Gmail.

---

## Features

- Monitors the Nashville Fire Department ArcGIS REST API
- Runs automatically every 5 minutes using GitHub Actions
- Detects incidents containing:
  - EN41
  - EN42
- Sends HTML email notifications
- Prevents duplicate alerts
- Logs all activity
- Gracefully handles API failures
- Uses GitHub Secrets for credentials
- Compatible with Python 3.12

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── monitor.yml
├── data/
│   └── alerted_incidents.json
├── logs/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── emailer.py
│   ├── logger.py
│   ├── monitor.py
│   └── state.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## GitHub Secrets

Create the following repository secrets under:

**Settings → Secrets and variables → Actions**

| Secret | Description |
|---------|-------------|
| `EMAIL_USERNAME` | Gmail address used to send email |
| `EMAIL_PASSWORD` | Gmail App Password |
| `EMAIL_RECIPIENT` | Recipient email address |

Example:

EMAIL_USERNAME=youraccount@gmail.com

EMAIL_PASSWORD=xxxxxxxxxxxxxxxx

EMAIL_RECIPIENT=captcollins777@gmail.com

---

## Gmail Requirements

Google no longer allows normal account passwords for SMTP.

Use a **Google App Password**:

1. Enable Two-Factor Authentication.
2. Visit Google Account → Security.
3. Open **App Passwords**.
4. Create a Mail App Password.
5. Store the generated password as:

EMAIL_PASSWORD

---

## Running Locally

Create a virtual environment.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Set environment variables.

Windows PowerShell:

```powershell
$env:EMAIL_USERNAME="your@gmail.com"
$env:EMAIL_PASSWORD="your_app_password"
$env:EMAIL_RECIPIENT="captcollins777@gmail.com"
```

Linux/macOS:

```bash
export EMAIL_USERNAME="your@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_RECIPIENT="captcollins777@gmail.com"
```

Run:

```bash
python src/monitor.py
```

---

## GitHub Actions

The included workflow runs automatically every five minutes.

It can also be started manually from the **Actions** tab using **Run workflow**.

---

## Duplicate Alert Prevention

The application stores alerted incident identifiers in:

```text
data/alerted_incidents.json
```

Only incidents that have **not previously generated an email** will trigger a notification.

---

## Logging

Runtime logs are written to:

```text
logs/
```

The log records:

- startup
- API requests
- incidents found
- emails sent
- duplicate suppression
- errors
- retries
- unexpected exceptions

---

## Email Contents

Each notification contains:

- Incident Number
- Dispatch Time
- Incident Type
- Address (when available)
- Units Dispatched
- Direct link to the incident (when available)

---

## Python Version

Python 3.12

---

## License

MIT
