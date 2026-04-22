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
            mail.login(self.sender_email, self.password)
            mail.select("inbox")
            
            status, messages = mail.search(None, 'UNSEEN')
            for num in messages[0].split():
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                
                content = ""
                if msg.is_multipart():
                    # Loop through the email parts to find the text body
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode().lower()
                            break
                else:
                    content = msg.get_payload(decode=True).decode().lower()

                if "yes" in content:
                    print("DEBUG: Found YES in email body!")
                    self.waiting_for_reply = False # Stop looking
                    mail.logout()
                    return True
            mail.logout()
        except Exception as e: 
            print(f"IMAP Error: {e}")
        return False
    

    def send_receipt_email(self, customer_email, receipt_data):
        # Build the dynamic list of products
        items_text = ""
        for item in receipt_data.get('items', []):
            items_text += f"- {item['product_name']}: ${item['product_price']:.2f}\n"
        
        # Body of the email


        body = f"""
Thank you for your purchase at Smart Makeup Store!\n
Items Purchased:
---------------------------------

{items_text}
---------------------------------
Subtotal: ${receipt_data['subtotal']:.2f}
GST (5%): ${receipt_data['gst']:.2f}
QST (9.975%): ${receipt_data['qst']:.2f}
Total: ${receipt_data['total']:.2f}

Date: {receipt_data['timestamp']}

Thank you for shopping with us!
        """
        msg = MIMEText(body)
        msg["Subject"] = "Your receipt from Smart Makeup Store"
        msg["From"] = self.sender_email
        msg["To"] = customer_email

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                # Send the message
                server.send_message(msg)
            self.last_email_time = time.time()
            print(f"Receipt sent successfully to {customer_email}")
            # Start checking for a reply
        except Exception as e:
            print(f"Email Send Error: {e}")
