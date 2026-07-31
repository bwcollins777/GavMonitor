"""
HTML email delivery for NFD Unit Monitor.
"""

from __future__ import annotations

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
from api import Incident

log = get_logger(__name__)


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
    background:#f5f5f5;
    margin:0;
    padding:25px;
}}

.container {{
    max-width:700px;
    margin:auto;
    background:white;
    border-radius:8px;
    border:1px solid #dddddd;
    overflow:hidden;
}}

.header {{
    background:#b71c1c;
    color:white;
    padding:18px;
}}

.header h2 {{
    margin:0;
}}

.content {{
    padding:20px;
}}

table {{
    border-collapse:collapse;
    width:100%;
}}

td {{
    padding:10px;
    border-bottom:1px solid #eeeeee;
}}

.label {{
    width:180px;
    font-weight:bold;
    background:#fafafa;
}}

.footer {{
    padding:18px;
    font-size:12px;
    color:#777777;
    background:#fafafa;
}}

.button {{
    display:inline-block;
    margin-top:18px;
    padding:12px 18px;
    background:#b71c1c;
    color:white;
    text-decoration:none;
    border-radius:4px;
}}
</style>
</head>

<body>

<div class="container">

<div class="header">
<h2>Nashville Fire Department Alert</h2>
</div>

<div class="content">

<p>
A monitored unit has been dispatched on a <strong>new incident</strong>.
</p>

<table>

<tr>
<td class="label">Incident Number</td>
<td>{incident.incident_number}</td>
</tr>

<tr>
<td class="label">Dispatch Time</td>
<td>{incident.dispatch_time}</td>
</tr>

<tr>
<td class="label">Incident Type</td>
<td>{incident.incident_type}</td>
</tr>

<tr>
<td class="label">Address</td>
<td>{incident.address}</td>
</tr>

<tr>
<td class="label">Units Dispatched</td>
<td>{incident.units}</td>
</tr>

</table>

<a class="button"
href="{incident.incident_link}">
View Active Incidents
</a>

</div>

<div class="footer">
Generated automatically by the
<strong>NFD Unit Monitor</strong>.
</div>

</div>

</body>
</html>
"""


def _build_text(incident: Incident) -> str:
    """
    Plain-text version for mail clients that do not render HTML.
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

Units:
{incident.units}

Active Incidents:
{incident.incident_link}
"""


def send_email(incident: Incident) -> None:
    """
    Send an HTML notification email.

    Raises:
        smtplib.SMTPException
            If delivery fails.
    """

    log.info(
        "Sending notification for incident %s",
        incident.incident_number,
    )

    message = EmailMessage()

    message["Subject"] = (
        f"NFD Alert - {incident.incident_number}"
    )

    message["From"] = EMAIL_USERNAME
    message["To"] = EMAIL_RECIPIENT

    message.set_content(_build_text(incident))
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
        "Notification email sent successfully."
    )
