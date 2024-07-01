import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(recipient_email, attachment_file, email_body):
    from_email = "job.automationtest@gmail.com"
    password = "uqja arkf lvkb tjnf"  # This is an app password, not the actual Gmail password
    subject = "Your Job Search Results"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Email body
    msg.attach(MIMEText(email_body, "plain"))

    # Attach the CSV file
    with open(attachment_file, "rb") as file:
        attachment = MIMEApplication(file.read(), _subtype="csv")
        attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment_file))
        msg.attach(attachment)

    # Connect to SMTP server and send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, recipient_email, msg.as_string())
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False