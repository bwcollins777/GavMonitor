# GavMonitor

GavMonitor is a production-quality cloud application that monitors the Nashville Fire Department Active Incidents ArcGIS REST API every five minutes using GitHub Actions.

When a **new** incident includes **EN41** or **EN42** in the `Unit_ID` field, GavMonitor sends a professional HTML email notification through Gmail.

---

## Features

- Python 3.12
- GitHub Actions automation
- Direct ArcGIS REST API queries
- No webpage scraping
- Monitors EN41 and EN42
- Duplicate alert prevention
- HTML email notifications
- Detailed logging
- Automatic retry of transient API failures
- Gmail SMTP using GitHub Secrets

---

## Repository Structure

```text
GavMonitor/
│
├── .github/
│   └── workflows/
│       └── monitor.yml
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── emailer.py
│   ├── logger.py
│   ├── models.py
│   ├── monitor.py
│   └── state.py
│
├── data/
│   └── alerted_incidents.json
│
├── logs/
│   └── .gitkeep
│
├── tests/
│
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

# Requirements

- Python 3.12
- GitHub account
- Gmail account with App Password enabled

---

# GitHub Secrets

Create the following repository secrets.

Repository

Settings

Secrets and variables

Actions

Add:

| Name | Value |
|------|-------|
| EMAIL_USERNAME | Gmail address used to send alerts |
| EMAIL_PASSWORD | Gmail App Password |
| EMAIL_RECIPIENT | Destination email address |

Example:

```
EMAIL_USERNAME=yourgmail@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
EMAIL_RECIPIENT=captcollins777@gmail.com
```

---

# Gmail App Password

Google requires an App Password for SMTP.

1. Enable Two-Factor Authentication.
2. Open Google Account.
3. Security.
4. App Passwords.
5. Create a password named:

```
GavMonitor
```

Store the generated password as the GitHub Secret:

```
EMAIL_PASSWORD
```

---

# Running Locally

Create a virtual environment.

Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Set environment variables.

Windows PowerShell

```powershell
$env:EMAIL_USERNAME="your@gmail.com"
$env:EMAIL_PASSWORD="yourapppassword"
$env:EMAIL_RECIPIENT="captcollins777@gmail.com"
```

Linux/macOS

```bash
export EMAIL_USERNAME="your@gmail.com"
export EMAIL_PASSWORD="yourapppassword"
export EMAIL_RECIPIENT="captcollins777@gmail.com"
```

Run the application.

```bash
python src/monitor.py
```

---

# GitHub Actions

The included workflow executes automatically every five minutes.

It may also be started manually from the Actions tab.

---

# Duplicate Alert Prevention

Previously alerted incident numbers are stored in:

```
data/alerted_incidents.json
```

Each incident generates only one email while it remains active.

Inactive incidents are automatically removed from the state file.

---

# Logging

Logs are written to:

```
logs/monitor.log
```

Each run records:

- Startup
- API requests
- Retry attempts
- Incidents retrieved
- Matching incidents
- Emails sent
- Duplicate suppression
- Errors
- Summary statistics

---

# Email Contents

Each notification contains:

- Incident Number
- Dispatch Time
- Incident Type
- Address (if available from the API)
- Units Dispatched
- Link to the Nashville Active Incidents page

---

# Verified ArcGIS Fields

The application uses only these verified fields:

- event_number
- Unit_ID
- incident_type_id
- DispatchDateTime

---

# License

MIT
