import smtplib
from pymongo import MongoClient
from email.mime.text import MIMEText
import os

# MongoDB Configuration
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["sample-email"]
collection = db["Users"]

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "cpr.bot.ai@gmail.com"
EMAIL_PASSWORD = "balx rhmo elrn rkgq"  # Replace with environment variable in production

# Fetch all email and password fields
users = collection.find({}, {"email": 1, "password": 1, "_id": 0})

def send_email(to_email, user_password):
    """Function to send email with login credentials."""
    subject = "Your Account Credentials"
    body = f"Hello,\n\nHere are your login details:\nEmail: {to_email}\nPassword: {user_password}\n\nPlease keep your credentials secure."
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    try:
        # Set up SMTP connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Corrected Login Credentials
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")

# Iterate over users and send emails
for user in users:
    email = user.get("email")
    password = user.get("password")

    if email and password:
        send_email(email, password)
    else:
        print(f"⚠ Skipping invalid data: Email={email}, Password={password}")

print("✅ All emails processed successfully.")
