from flask import current_app, url_for
from flask_mail import Message
import imaplib
import email
from email.header import decode_header

# Sending an email to the newly registered customer to verify their account
def send_registration_email(first_name, last_name, email_address, customer_id):
    
    # Generate verification URL dynamically for this customer
    verification_url = url_for('store.customerVerification', customer_id=customer_id, _external=True)

    # Compose the email message
    msg = Message(
        subject="Welcome to the Smart Store!",  # subject of the email
        sender=current_app.config['MAIL_USERNAME'], # refers to our store's email from app config
        recipients=[email_address] # recipient is the newly registered customer's email
    )

    # Composing message to be sent
    # plain text fallback
    msg.body = f"Hello {first_name} {last_name},\nPlease verify your account: {verification_url}"

    # HTML version
    msg.html = f"""
    Hello {first_name} {last_name},<br><br>
    Thank you for registering for our Smart Store!<br>
    Please click <a href="{verification_url}">here</a> to verify your account.<br><br>
    Regards,<br>The Smart Store Team
    """

    # Send the email using the Mail instance attached to current_app
    try:
        current_app.extensions['mail'].send(msg)
        print("Customer verification email sent successfully!")  # for debugging
    except Exception as e:
        print("Customer added, but failed to send verification email. Please contact support.")
        print("Email error:", e)  # debug info for why sending failed


# Sending a notification to the store inbox when a new customer verifies
def send_new_customer_notification(first_name, last_name, email_address):
    
    msg = Message(
        subject="New Customer Verified!",  # subject of the notification
        sender=current_app.config['MAIL_USERNAME'],  # sender = store email
        recipients=[current_app.config['MAIL_USERNAME']]  # sending to store inbox
    )

    # plain text message
    msg.body = f"Customer {first_name} {last_name} ({email_address}) has just verified their account."

    # HTML version
    msg.html = f"""
    <b>New Customer Verified!</b><br>
    Name: {first_name} {last_name}<br>
    Email: {email_address}<br>
    """

    # Send the email using Flask-Mail
    try:
        current_app.extensions['mail'].send(msg)
        print("Store notification email sent successfully!")
    except Exception as e:
        print("Failed to send store notification email:", e)


# Reading emails from the store inbox
def fetch_store_emails():
    """
    Connects to Gmail using IMAP and fetches all emails from the inbox.
    Returns a list of dicts with keys: subject, from, body
    """
    emails = []
    username = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    try:
        # connecting to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")  # select inbox
        
        # searching for all messages
        status, messages = mail.search(None, "ALL")
        message_numbers = messages[0].split()

        for num in reversed(message_numbers):  # iterate from newest to oldest
            status, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]

            msg = email.message_from_bytes(raw_email)

            # decoding subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            # decoding sender
            from_ = msg.get("From")

            # decoding email body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_dispo = str(part.get("Content-Disposition"))

                    # skip attachments
                    if content_type == "text/plain" and "attachment" not in content_dispo:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            emails.append({
                "subject": subject,
                "from": from_,
                "body": body
            })

        mail.logout()

    except Exception as e:
        print("Error fetching store emails:", e)

    return emails