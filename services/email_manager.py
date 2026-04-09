import smtplib, imaplib, email, time
from email.mime.text import MIMEText

class EmailAlertSystem:
    def __init__(self, sender_email, password, receiver_email):
        self.sender_email = sender_email
        self.password = password
        self.receiver_email = receiver_email
        self.last_email_time = 0
        self.waiting_for_reply = False

    def send_alert(self, temp, fridge):
        body = f"The current temperature in {fridge} is {temp}°C. Would you like to turn on the fan? (Reply YES or NO)"
        msg = MIMEText(body)
        msg["Subject"] = "Temperature Alert"
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                # Send the message
                server.send_message(msg)
            self.last_email_time = time.time()
            # Start checking for a reply
            self.waiting_for_reply = True
        except Exception as e:
            print(f"Email Send Error: {e}")

    def check_for_yes(self):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            # Login to inbox to check for reply
            mail.login(self.sender_email, self.password)
            mail.select("inbox")
            # Look for unseen messages from sender email
            status, messages = mail.search(None, 'UNSEEN')
            for num in messages[0].split():
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                content = msg.get_payload(decode=True).decode().lower() if not msg.is_multipart() else ""
                if "yes" in content:
                    self.waiting_for_reply = False
                    return True
            mail.logout()
        except: pass
        return False
    

    def send_receipt_email(self, customer_email):
        body = f"Thank you for your purchase!"
        msg = MIMEText(body)
        msg["Subject"] = "Receipt Alert"
        msg["From"] = self.sender_email
        msg["To"] = customer_email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                # Send the message
                server.send_message(msg)
            self.last_email_time = time.time()
            # Start checking for a reply
        except Exception as e:
            print(f"Email Send Error: {e}")
