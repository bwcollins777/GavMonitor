"""
Email delivery for GavMonitor.

Builds and sends professional HTML email notifications using Gmail SMTP.
"""

from __future__ import annotations

import html
import smtplib
import ssl
from email.message import EmailMessage

from config import (
    EMAIL_PASSWORD,
    EMAIL_RECIPIENT,
    EMAIL_USERNAME,
    SMTP_PORT,
    SMTP_SERVER,
)
from logger import get_logger
from models import Incident

log = get_logger(__name__)


def _escape(value: str) -> str:
    """
    HTML-escape a string.
    """

    return html.escape(value or "")


def _build_html(incident: Incident) -> str:
    """
    Build the HTML email body.
    """

    return f"""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>

body {{
    font-family: Arial, Helvetica, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 24px;
}}

.container {{
    max-width: 720px;
    margin: auto;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #dddddd;
}}

.header {{
    background: #b71c1c;
    color: white;
    padding: 18px;
}}

.header h2 {{
    margin: 0;
}}

.content {{
    padding: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #ececec;
}}

.label {{
    width: 180px;
    font-weight: bold;
    background: #fafafa;
}}

.button {{
    display: inline-block;
    margin-top: 20px;
    padding: 12px 18px;
    background: #b71c1c;
    color: white;
    text-decoration: none;
    border-radius: 4px;
}}

.footer {{
    padding: 18px;
    font-size: 12px;
    color: #666666;
    background: #fafafa;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">
<h2>🚒 Nashville Fire Department Alert</h2>
</div>

<div class="content">

<p>
A monitored unit has been dispatched on a <strong>new incident</strong>.
</p>

<table>

<tr>
<td class="label">Incident Number</td>
<td>{_escape(incident.incident_number)}</td>
</tr>

<tr>
<td class="label">Dispatch Time</td>
<td>{_escape(incident.dispatch_time)}</td>
</tr>

<tr>
<td class="label">Incident Type</td>
<td>{_escape(incident.incident_type)}</td>
</tr>

<tr>
<td class="label">Address</td>
<td>{_escape(incident.address)}</td>
</tr>

<tr>
<td class="label">Units Dispatched</td>
<td>{_escape(incident.units)}</td>
</tr>

</table>

<a class="button"
href="{incident.incident_link}">
View Active Incidents
</a>

</div>

<div class="footer">
Generated automatically by GavMonitor.
</div>

</div>

</body>
</html>
"""


def _build_text(incident: Incident) -> str:
    """
    Plain-text fallback for mail clients that do not render HTML.
    """

    return f"""\
Nashville Fire Department Alert

A monitored unit has been dispatched.

Incident Number:
{incident.incident_number}

Dispatch Time:
{incident.dispatch_time}

Incident Type:
{incident.incident_type}

Address:
{incident.address}

Units Dispatched:
{incident.units}

View Active Incidents:
{incident.incident_link}
"""


def send_email(incident: Incident) -> None:
    """
    Send an email notification.

    Raises
    ------
    smtplib.SMTPException
        If delivery fails.
    """

    log.info(
        "Sending email for incident %s.",
        incident.incident_number,
    )

    message = EmailMessage()

    message["Subject"] = incident.email_subject
    message["From"] = EMAIL_USERNAME
    message["To"] = EMAIL_RECIPIENT

    message.set_content(
        _build_text(incident)
    )

    message.add_alternative(
        _build_html(incident),
        subtype="html",
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT,
        context=context,
    ) as smtp:

        smtp.login(
            EMAIL_USERNAME,
            EMAIL_PASSWORD,
        )

        smtp.send_message(message)

    log.info(
        "Email successfully sent for incident %s.",
        incident.incident_number,
    )
