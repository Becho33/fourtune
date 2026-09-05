import smtplib
from email.message import EmailMessage

from flask import current_app


def send_booking_notification(booking):
    """Notify the business of a booking; return False when mail is not configured."""
    config = current_app.config
    required = (config.get("MAIL_SERVER"), config.get("MAIL_FROM"), config.get("BOOKING_NOTIFICATION_EMAIL"))
    if not all(required):
        current_app.logger.info("Booking email notification skipped: mail is not configured")
        return False

    message = EmailMessage()
    message["Subject"] = f"New Riina Kushu booking request #{booking.id}"
    message["From"] = config["MAIL_FROM"]
    message["To"] = config["BOOKING_NOTIFICATION_EMAIL"]
    message.set_content(
        "\n".join(
            [
                f"A new booking request has been received.",
                f"Reference: #{booking.id}",
                f"Name: {booking.name}",
                f"Email: {booking.email}",
                f"Phone: {booking.phone or 'Not provided'}",
                f"Reading: {booking.service}",
                f"Preferred date: {booking.preferred_date or 'Not specified'}",
                f"Preferred time: {booking.preferred_time or 'Not specified'}",
                "",
                f"Message: {booking.message or 'None'}",
            ]
        )
    )

    with smtplib.SMTP(config["MAIL_SERVER"], config["MAIL_PORT"], timeout=10) as smtp:
        if config["MAIL_USE_TLS"]:
            smtp.starttls()
        if config["MAIL_USERNAME"]:
            smtp.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
        smtp.send_message(message)
    return True
