from flask import current_app, url_for
from flask_mail import Message

def send_registration_email(first_name, last_name, email_address, customer_id):
    verification_url = url_for('store.customerVerification', customer_id=customer_id, _external=True)
    msg = Message(
        subject="Welcome to the Smart Store!",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email_address]
    )
    msg.body = f"Hello {first_name} {last_name},\nPlease verify your account: {verification_url}"
    msg.html = f"""
    Hello {first_name} {last_name},<br><br>
    Thank you for registering for our Smart Store!<br>
    Please click <a href="{verification_url}">here</a> to verify your account.<br><br>
    Regards,<br>The Smart Store Team
    """
    try:
        current_app.extensions['mail'].send(msg)
        print("Customer verification email sent successfully!")
    except Exception as e:
        print("Customer added, but failed to send verification email:", e)

def send_new_customer_notification(first_name, last_name, email_address):
    msg = Message(
        subject="New Customer Verified!",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config['MAIL_USERNAME']]
    )
    msg.body = f"Customer {first_name} {last_name} ({email_address}) has just verified their account."
    msg.html = f"""
    <b>New Customer Verified!</b><br>
    Name: {first_name} {last_name}<br>
    Email: {email_address}<br>
    """
    try:
        current_app.extensions['mail'].send(msg)
        print("Store notification email sent successfully!")
    except Exception as e:
        print("Failed to send store notification email:", e)

def send_system_alert_email(title, message):
    """
    Generic system alert email. Sends to the store inbox (MAIL_USERNAME)
    """
    msg = Message(
        subject=title,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config['MAIL_USERNAME']]
    )
    msg.body = message
    msg.html = f"<b>{title}</b><br><pre>{message}</pre>"
    try:
        current_app.extensions['mail'].send(msg)
        print("System alert email sent successfully!")
    except Exception as e:
        print(f"Failed to send system alert email: {e}")

def send_threshold_update_email(fridge, t_min, t_max, h_min, h_max):
    title = f"Threshold Updated - Fridge {fridge}"
    message = f"Temperature: {t_min}-{t_max} °C\nHumidity: {h_min}-{h_max} %"
    send_system_alert_email(title, message)

def send_security_alert_notification(temperature):
    title = "[⚠️] Security Alert - Abnormal Temperature Detected"
    message = f"The system detected an irregular temperature reading: {temperature} °C"
    send_system_alert_email(title, message)

import imaplib
import email
from email.header import decode_header

def fetch_store_emails():
    emails = []
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        message_numbers = messages[0].split()

        for num in reversed(message_numbers):
            status, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            from_ = msg.get("From")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_dispo = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_dispo:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({"subject": subject, "from": from_, "body": body})

        mail.logout()
    except Exception as e:
        print("Error fetching store emails:", e)

    return emails