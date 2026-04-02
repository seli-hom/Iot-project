# email_service.py
from flask import current_app, url_for
from flask_mail import Message
from models.database import getDB
import imaplib
import email
from email.header import decode_header

# -----------------------------
# Helper function: Get users by role
# -----------------------------
def get_users_by_roles(roles):
    db = getDB()
    placeholders = ','.join(['?'] * len(roles))
    query = f'''
        SELECT email FROM customers
        WHERE role IN ({placeholders})
        AND verified = 1
    '''
    users = db.execute(query, roles).fetchall()
    db.close()
    return [u["email"] for u in users]


# -----------------------------
# Base email sending service
# -----------------------------
def send_email(subject, body, html=None, recipients=None, roles=None):
    """
    recipients = explicit list
    roles = ['admin', 'employee','customer']
    """

    if roles:
        role_recipients = get_users_by_roles(roles)
        if recipients:
            recipients = list(set(recipients + role_recipients))
        else:
            recipients = role_recipients

    if not recipients:
        print("[ERROR] No recipients found. The email was not sent.")
        return

    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=recipients
    )

    msg.body = body
    msg.html = html if html else body

    try:
        current_app.extensions['mail'].send(msg)
        print(f"[SUCCESS] Email was sent to {len(recipients)} users")
    except Exception as e:
        print("[ERROR] Email has failed to send:", e)


# -----------------------------
# Send registration email
# -----------------------------
def send_registration_email(user_fname, user_lname, user_email, user_id):
    verification_url = url_for('store.customerVerification', user_id=user_id, _external=True)
    send_email(
        "Welcome to the Smart Store!",
        f"Verify: {verification_url}",
        f"""
        Hello {user_fname} {user_lname},<br><br>
        Please verify your account:<br>
        <a href="{verification_url}">Verify Account</a>
        """,
        recipients=[user_email]
    )


# -----------------------------
# New customer notification for admins
# -----------------------------
def send_new_customer_notification(user_fname, user_lname, user_email):
    send_email(
        "New Customer Verified",
        f"{user_fname} {user_lname} verified",
        f"""
        <b>New Customer Verified</b><br>
        {user_fname} {userq}<br>
        {user_email}
        """,
        roles=["admin"]
    )


# -----------------------------
# Fan toggle email
# -----------------------------
def send_fan_toggle_email(is_on):
    status = "ON" if is_on else "OFF"

    fan_on_url = url_for('store.fan_on_link', _external=True)
    fan_off_url = url_for('store.fan_off_link', _external=True)

    send_email(
        f"Fan Turned {status}",
        f"Fan is now {status}",
        f"""
        <b>Fan Turned {status}</b><br><br>
        Control Fan:<br><br>
        <a href="{fan_on_url}" style="padding:10px;background:#28a745;color:white;border-radius:5px;text-decoration:none;">
            Turn ON
        </a><br><br>
        <a href="{fan_off_url}" style="padding:10px;background:#dc3545;color:white;border-radius:5px;text-decoration:none;">
            Turn OFF
        </a>
        """,
        roles=["admin", "employee"]
    )


# -----------------------------
# Threshold update email
# -----------------------------
def send_threshold_update_email(fridge, t_min, t_max, h_min, h_max):
    fan_on_url = url_for('store.fan_on_link', _external=True)
    fan_off_url = url_for('store.fan_off_link', _external=True)

    send_email(
        f"Fridge {fridge} Alert",
        "Threshold exceeded",
        f"""
        <b>Fridge {fridge} Alert</b><br><br>
        Temp: {t_min}-{t_max} °C<br>
        Humidity: {h_min}-{h_max} %<br><br>
        <b>Fan Controls:</b><br><br>
        <a href="{fan_on_url}" style="padding:10px;background:#28a745;color:white;border-radius:5px;">
            Turn Fan ON
        </a><br><br>
        <a href="{fan_off_url}" style="padding:10px;background:#dc3545;color:white;border-radius:5px;">
            Turn Fan OFF
        </a>
        """,
        roles=["admin", "employee"]
    )


# -----------------------------
# Security alert email
# -----------------------------
def send_security_alert_notification(temperature):
    if temperature <= 0:
        status = "Freezing Risk"
        color = "#0dcaf080"
        icon = "bi-snow"
    elif temperature >= 10:
        status = "Overheating Risk"
        color = "#dc354580"
        icon = "bi-thermometer-high"
    else:
        status = "Normal"
        color = "#28a74580"
        icon = "bi-check-circle"

    send_email(
        "Security Alert - Temperature Issue",
        f"Temperature issue: {temperature}",
        f"""
        <div style="font-family:Arial;">
            <b>Security Alert</b><br><br>
            <i class="{icon}" style="color:{color};"></i>
            Temperature: {temperature} °C<br>
            Status: <b style="color:{color};">{status}</b>
        </div>
        """,
        roles=["admin", "employee"]
    )


# -----------------------------
# Fetch emails from inbox
# -----------------------------
def fetch_store_emails():
    emails = []
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")

        for num in reversed(messages[0].split()):
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            # SUBJECT
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            # FROM
            sender = msg.get("From")
            # BODY
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            emails.append({
                "subject": subject,
                "from": sender,
                "body": body
            })
        mail.logout()
    except Exception as e:
        print("Error fetching emails:", e)
    return emails