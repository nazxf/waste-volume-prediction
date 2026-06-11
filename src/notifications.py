"""
Notification helpers for Phase 2 alerts.

Email and SMS sending are optional. If credentials are not configured, helpers
return a dry-run result instead of failing the prediction flow.
"""
from dataclasses import asdict, dataclass
from email.message import EmailMessage
import os
import smtplib
from typing import Dict, Iterable, List, Optional
from urllib import parse, request


@dataclass
class NotificationResult:
    channel: str
    sent: bool
    dry_run: bool
    message: str

    def to_dict(self) -> Dict:
        return asdict(self)


def build_prediction_alert(
    predicted_volume: float,
    threshold: float,
    date: str,
    fleet_recommendation: Optional[Dict] = None
) -> str:
    """Build a concise operational alert message."""
    fleet_text = ""
    if fleet_recommendation:
        fleet_text = (
            f" Recommended fleet: {fleet_recommendation.get('trucks_needed')} trucks "
            f"at {fleet_recommendation.get('utilization_rate')}% utilization."
        )

    return (
        f"Waste prediction alert for {date}: {predicted_volume:.2f} tons "
        f"(threshold {threshold:.2f} tons).{fleet_text}"
    )


def _split_recipients(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def send_email_notification(
    subject: str,
    body: str,
    recipients: Optional[Iterable[str]] = None,
    dry_run: bool = False
) -> NotificationResult:
    """Send an email notification using SMTP environment variables."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", smtp_username or "no-reply@wastepredict.local")
    recipient_list = list(recipients or _split_recipients(os.getenv("NOTIFICATION_RECIPIENTS")))

    if dry_run or not (smtp_host and recipient_list):
        return NotificationResult(
            channel="email",
            sent=False,
            dry_run=True,
            message="Email dry run: SMTP_HOST and recipients are required to send.",
        )

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = ", ".join(recipient_list)
    email.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        server.send_message(email)

    return NotificationResult(
        channel="email",
        sent=True,
        dry_run=False,
        message=f"Email sent to {len(recipient_list)} recipient(s).",
    )


def send_sms_notification(
    body: str,
    recipients: Optional[Iterable[str]] = None,
    dry_run: bool = False
) -> NotificationResult:
    """
    Send SMS through Twilio-compatible environment variables.

    Required env vars for real sending: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER, and SMS_RECIPIENTS or explicit recipients.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    recipient_list = list(recipients or _split_recipients(os.getenv("SMS_RECIPIENTS")))

    if dry_run or not (account_sid and auth_token and from_number and recipient_list):
        return NotificationResult(
            channel="sms",
            sent=False,
            dry_run=True,
            message="SMS dry run: Twilio credentials, sender, and recipients are required to send.",
        )

    sent_count = 0
    for recipient in recipient_list:
        data = parse.urlencode({
            "From": from_number,
            "To": recipient,
            "Body": body,
        }).encode("utf-8")
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        req = request.Request(url, data=data)
        password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, account_sid, auth_token)
        auth_handler = request.HTTPBasicAuthHandler(password_manager)
        opener = request.build_opener(auth_handler)
        with opener.open(req, timeout=20):
            sent_count += 1

    return NotificationResult(
        channel="sms",
        sent=True,
        dry_run=False,
        message=f"SMS sent to {sent_count} recipient(s).",
    )


def send_prediction_notifications(
    predicted_volume: float,
    threshold: float,
    date: str,
    fleet_recommendation: Optional[Dict] = None,
    channels: Optional[Iterable[str]] = None,
    dry_run: bool = False
) -> List[Dict]:
    """Send configured prediction alerts for selected channels."""
    channels = list(channels or ["email"])
    body = build_prediction_alert(predicted_volume, threshold, date, fleet_recommendation)
    subject = "Waste volume prediction alert"
    results = []

    if "email" in channels:
        results.append(send_email_notification(subject, body, dry_run=dry_run).to_dict())
    if "sms" in channels:
        results.append(send_sms_notification(body, dry_run=dry_run).to_dict())

    return results


