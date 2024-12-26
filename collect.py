from flask import Flask, request, jsonify
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/')
db = client['CPR-Details']
users_collection = db['Users']       # Collection storing admins, leads, and other users
feedback_collection = db['feedbacks']  # Collection for storing feedback

# SMTP settings (Gmail in this example)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'your-email@gmail.com'  # Replace with your SMTP email
SMTP_PASSWORD = 'your-email-password'  # Replace with your SMTP password


def send_email(from_email, to_email, subject, text_content):
    """
    Sends an email via the configured SMTP server.
    """
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = f"{text_content}\n\n-- From: {from_email}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    """
    Endpoint to send feedback from an admin/lead to a student.
    """
    data = request.get_json()

    # Extract the required data
    from_email = data.get('from')  # Sender's email
    to_email = data.get('to')  # Student's email
    subject = data.get('subject')
    text_content = data.get('textcontent')

    # Validate input
    if not from_email or not to_email or not subject or not text_content:
        return jsonify({"error": "Missing required fields"}), 400

    # Verify sender is an admin or lead
    sender = users_collection.find_one({"email": from_email, "role": {"$in": ["admin", "lead"]}})
    if not sender:
        return jsonify({"error": f"Sender {from_email} is not authorized to send feedback"}), 403

    # Store feedback in the database
    feedback = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "textcontent": text_content,
        "date": datetime.datetime.utcnow()  # Store feedback date
    }
    feedback_collection.insert_one(feedback)

    # Send the feedback email
    email_sent = send_email(from_email, to_email, subject, text_content)

    if email_sent:
        return jsonify({"message": "Feedback sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send feedback"}), 500


@app.route('/get-feedbacks', methods=['GET'])
def get_feedbacks():
    """
    Endpoint to fetch all feedbacks from the database.
    """
    try:
        feedbacks = list(feedback_collection.find({}, {'_id': 0}))  # Exclude the MongoDB `_id` field
        return jsonify(feedbacks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-users', methods=['GET'])
def get_users():
    """
    Endpoint to fetch all users with roles 'admin' and 'lead'.
    """
    try:
        users = list(users_collection.find({"role": {"$in": ["admin", "lead"]}}, {"_id": 0, "email": 1, "role": 1}))
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,port=5003)
