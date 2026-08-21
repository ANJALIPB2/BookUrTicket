import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import os

# ==========================================
# 📧 REAL EMAIL CONFIGURATION
# =========================================

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ENABLE_REAL_EMAILS = True

def send_email_async(to_email, subject, body, attachment_path=None):
    if not ENABLE_REAL_EMAILS:
        print(f"\n--- EMAIL NOTIFICATION SIMULATION ---")
        print(f"To: {to_email}\nSubject: {subject}\nBody: {body}\nAttachment: {attachment_path}")
        print(f"-------------------------------------\n")
        return

    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg.attach(MIMEText(body))

        if attachment_path and os.path.exists(attachment_path):
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[SUCCESS] Real email sent to {to_email} (with attachment: {attachment_path})")
    except Exception as e:
        print(f"[FAILED] Could not send real email. Error: {str(e)}")

def trigger_email(to_email, subject, body, attachment_path=None):
    t = threading.Thread(target=send_email_async, args=(to_email, subject, body, attachment_path))
    t.start()

