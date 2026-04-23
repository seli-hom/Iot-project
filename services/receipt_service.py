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
    

    def send_receipt_email(self, customer_email, receipt_data):
        # Build the dynamic list of products
        items_text = ""
        for item in receipt_data.get('items', []):
            items_text += f"- {item['product_name']}: ${item['product_price']:.2f}\n"
        print(receipt_data)
        points_info = ""
        # Body of the email
        if receipt_data['total_points'] is not None:
            points_info = f"You have a total of {receipt_data['total_points']} loyalty points. \n"
            if receipt_data['total_points'] < 50 :
                points_info += f"Only {50 - receipt_data['total_points']} more points until you can get a 5$ discount on your next purchase!\n"
        else:
            points_info = f"You earned {receipt_data['purchase_points']} loyalty points with this purchase. Sign up for an account to start earning points towards discounts on future purchases!\\n"
        body = f"""
        Thank you for your purchase at Smart Makeup Store!\n
        Items Purchased:
        ---------------------------------

        {items_text}
        ---------------------------------

        {receipt_data['discount']}

        ---------------------------------
        Subtotal: ${receipt_data['subtotal']:.2f}
        GST (5%): ${receipt_data['gst']:.2f}
        QST (9.975%): ${receipt_data['qst']:.2f}
        Total: ${receipt_data['total']:.2f}

        Points Earned with purchase: {receipt_data['purchase_points']}

        {points_info}

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
            