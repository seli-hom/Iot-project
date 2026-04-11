from flask import current_app, url_for
from flask_mail import Message
from models.database import getDB
import imaplib
import email
from email.header import decode_header

def get_users_by_roles(roles):

    db = getDB()

    placeholders = ','.join(['?'] * len(roles))

    query = f'''
        SELECT user_email
        FROM users
        WHERE user_role IN ({placeholders})
        AND user_verified = 1
    '''

    users = db.execute(query, roles).fetchall()
    db.close()

    return [u["user_email"] for u in users]

def send_email(subject, body, html=None, recipients=None, roles=None):

    try:

        if roles:
            role_recipients = get_users_by_roles(roles)

            if recipients:
                recipients = list(set(recipients + role_recipients))
            else:
                recipients = role_recipients

        if not recipients:
            print("[EMAIL ERROR] No recipients found")
            return

        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients
        )

        msg.body = body
        msg.html = html if html else body

        print("[EMAIL] Sending to:", recipients)

        mail = current_app.extensions["mail"]
        mail.send(msg)

        print("[EMAIL SUCCESS] Sent")

    except Exception as e:
        import traceback
        print("[EMAIL ERROR]")
        traceback.print_exc()

def send_registration_email(user_fname, user_lname, user_email, user_id):

    verification_url = url_for(
        'store.customerVerification',
        user_id=user_id,
        _external=True
    )

    send_email(
        "Welcome to Smart Store",
        f"Verify your account: {verification_url}",
        f"""
        <h3>Welcome {user_fname} {user_lname}</h3>

        <p>Please verify your account:</p>

        <a href="{verification_url}"
        style="padding:12px;background:#d8aeb7;color:white;border-radius:6px;text-decoration:none;">
        Verify Account
        </a>
        """,
        recipients=[user_email]
    )

def send_new_customer_notification(user_fname, user_lname, user_email):

    send_email(
        "New Customer Verified",
        f"{user_fname} verified",
        f"""
        <h3>New Customer Verified</h3>

        Name: {user_fname} {user_lname}<br>
        Email: {user_email}
        """,
        roles=["admin"]
    )

def send_fan_toggle_email(is_on):

    status = "ON" if is_on else "OFF"

    send_email(
        f"Fan Turned {status}",
        f"Fan {status}",
        f"""
        <h3>Fan Turned {status}</h3>

        The fan has been turned {status}
        """,
        roles=["admin", "employee"]
    )

def send_threshold_update_email(fridge, t_min, t_max, h_min, h_max):

    send_email(
        f"Fridge {fridge} Alert",
        "Threshold exceeded",
        f"""
        <h3>Fridge {fridge} Alert</h3>

        Temperature: {t_min}-{t_max}°C<br>
        Humidity: {h_min}-{h_max}%
        """,
        roles=["admin", "employee"]
    )

def send_system_alert_email(title, message):

    send_email(
        title,
        message,
        f"""
        <h3>System Alert</h3>
        <p>{message}</p>
        """,
        roles=["admin", "employee"]
    )

def send_security_alert_notification(temperature):

    if temperature <= 0:
        status = "Freezing Risk"
    elif temperature >= 10:
        status = "Overheating Risk"
    else:
        status = "Normal"

    send_email(
        "Security Alert",
        f"Temperature {temperature}",
        f"""
        <h3>Security Alert</h3>

        Temperature: {temperature}°C<br>
        Status: {status}
        """,
        roles=["admin", "employee"]
    )

def fetch_store_emails():

    emails = []

    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    try:

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")

        for num in reversed(messages[0].split()[:10]):

            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            subject, encoding = decode_header(msg["Subject"])[0]

            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            sender = msg.get("From")

            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
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
        print("Inbox error:", e)

    return emails