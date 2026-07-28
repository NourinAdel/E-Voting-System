import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, receiver_email, password, subject, body):
    msg = MIMEMultipart()

    # Setting the email's fields.
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Create a plain MIME object to store the email's body.
    body = MIMEText(body, 'plain')
    msg.attach(body) # Attach it to the main message.

    server = None
    try:
        # Connect to gmail's SMTP server with TLS port 587
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() # Secure TLS.
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, msg.as_string())
        return True # If successful, return True.

    except Exception as e:
        return False
    finally:
        # Make sure server is always closed properly.
        if server is not None:
            server.quit()