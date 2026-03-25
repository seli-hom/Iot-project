from flask import current_app, url_for
from flask_mail import Message
from models.database import getDB

# getting users by their user role so we can send emails to specific groups
# and make sure that other groups i.e. customers do not see this information.
def get_users_by_roles(roles):
    db = getDB()

    # initializing the number of SQL placeholders based on the length of the roles list
    placeholders = ','.join(['?'] * len(roles))

    query = f'''
        SELECT email FROM customers
        WHERE role IN ({placeholders})
        AND verified = 1
    '''

    users = db.execute(query, roles).fetchall()
    db.close()

    return [u["email"] for u in users]


# base email sending service, to be reused to send different types of emails (see ln.50 and below)
# subject refers to the matter at hand, body refers to the content, html in case you want to include html in
# your email, you can either send an email to specific user roles or define recipients who will recieve the email
def send_email(subject, body, html=None, recipients=None, roles=None):
    """
    recipients = explicit list
    roles = ['admin', 'employee','customer']
    """

    # getting the users based on their roles if roles have been provided
    if roles:
        role_recipients = get_users_by_roles(roles)

        # if both are provided we add both together
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


# Sending an email to verify a newly registered user
# uses recipients, as you should only verify one user at a time
def send_registration_email(first_name, last_name, email_address, customer_id):
    verification_url = url_for('store.customerVerification', customer_id=customer_id, _external=True)

    send_email(
        "Welcome to the Smart Store!",
        f"Verify: {verification_url}",
        f"""
        Hello {first_name} {last_name},<br><br>
        Please verify your account:<br>
        <a href="{verification_url}">Verify Account</a>
        """,
        recipients=[email_address]
    )


# Sending an email to admin to alert to a new user being registered
# uses roles[] to only send to admin users
def send_new_customer_notification(first_name, last_name, email_address):
    send_email(
        "New Customer Verified",
        f"{first_name} {last_name} verified",
        f"""
        <b>New Customer Verified</b><br>
        {first_name} {last_name}<br>
        {email_address}
        """,
        roles=["admin"]
    )


# Sending an email to Admin users and employee users to alert them that the fan has been turned on/off
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


# Sending an email to Admin users and employee users to alert them that a threshold has been updated
# includes which fridge the threshold belongs to as well as which guage, and the current status of the fridge overall
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


# Sending an alert when the temperature reaches too high or too low
def send_security_alert_notification(temperature):
    # determining the alert type based on the temperature

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


# fetching emails from gmail inbox to be displayed on the site
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

        for num in reversed(messages[0].split()):
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({"subject": subject, "body": body})

        mail.logout()
    except Exception as e:
        print("Error fetching emails:", e)

    return emails