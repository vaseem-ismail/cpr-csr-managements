from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

#students
#admin

# MongoDB Configuration
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client["student_booking"]  # Database name
bookings_collection = db["bookings"]  # Collection for storing bookings

SectionA = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionB = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionC = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"  # Change to your SMTP provider
SMTP_PORT = 587
EMAIL_SENDER = "cpr.bot.ai@gmail.com"
EMAIL_PASSWORD = "blty ihcf xbwg ocgb"  # Use environment variables for security


def generate_default_slots():
    """Generate default time slots between 2 PM and 5 PM (6 slots, 30 minutes each)."""
    start_time = datetime.strptime("14:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    slots = []
    while start_time < end_time:
        slots.append({
            "time": start_time.strftime("%H:%M"),
            "booked": False,
            "student_id": None,
        })
        start_time += timedelta(minutes=30)
    return slots



@app.route("/calendar/<section>", methods=["GET"])
def get_calendar(section):
    """Return all upcoming dates for the current month with booking status."""
    calendar = []
    
    # Get today's date and the start of the current month
    today = datetime.now()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month.replace(month=today.month + 1) - timedelta(days=1)) if today.month < 12 else (start_of_month.replace(month=1) - timedelta(days=1))
    
    # Loop through each day in the current month
    current_day = start_of_month
    while current_day <= end_of_month:
        date_str = current_day.strftime("%Y-%m-%d")
        
        # Check if slots for this date already exist in the database
        slot_doc = bookings_collection.find_one({"section": section, "date": date_str})

        if not slot_doc:
            # If no slots exist, generate new slots and insert into the DB
            default_slots = generate_default_slots()
            new_slot_doc = {
                "section": section,
                "date": date_str,
                "slots": default_slots
            }
            bookings_collection.insert_one(new_slot_doc)
            slot_doc = new_slot_doc
        
        # Check if the slots are fully booked
        fully_booked = all(slot["booked"] for slot in slot_doc["slots"])
        
        # Append to the calendar data
        calendar.append({
            "date": date_str,
            "fully_booked": fully_booked
        })
        
        # Move to the next day
        current_day += timedelta(days=1)

    return jsonify({"calendar": calendar}), 200

def generate_slots(date):
    """Generate time slots between 2 PM and 5 PM (6 slots, 30 minutes each)."""
    base_time = datetime.strptime(f"{date} 14:00", "%Y-%m-%d %H:%M")
    return [
        {"time": (base_time + timedelta(minutes=30 * i)).strftime("%H:%M"), "booked": False}
        for i in range(6)
    ]

@app.route("/slots/<section>/<date>", methods=["GET"])
def get_slots(section, date):
    """Fetch slots for a given section and date."""
    slot_doc = bookings_collection.find_one({"section": section, "date": date})

    if not slot_doc:
        # Create default slots if no entry exists
        default_slots = generate_slots(date)
        new_slot_doc = {
            "section": section,
            "date": date,
            "slots": default_slots
        }
        bookings_collection.insert_one(new_slot_doc)
        slot_doc = new_slot_doc

    return jsonify({"slots": slot_doc["slots"]}), 200


def send_email(to_emails, subject, message):
    """Send an email notification."""
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(to_emails)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_emails, msg.as_string())
        print(f"Email sent to {to_emails}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route("/book_slot", methods=["POST"])
def book_slot():
    """Book a slot and send an email notification."""
    data = request.json
    section = data.get("section")
    date = data.get("date")
    time = data.get("time")
    student_id = data.get("student_id")
    # student_email = data.get("student_email")
    # student_name = data.get("student_name")

    if not section or not date or not time or not student_id or not student_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Update the slot to mark it as booked
    result = bookings_collection.update_one(
        {"section": section, "date": date, "slots.time": time, "slots.booked": False},
        {
            "$set": {
                "slots.$.booked": True,
                "slots.$.student_id": student_id
            }
        }
    )

    if result.matched_count > 0:
        # Email recipient selection
        admin_emails = []
        if section == "A":
            admin_emails = SectionA
        elif section == "B":
            admin_emails = SectionB
        elif section == "C":
            admin_emails = SectionC

        # Email Content
        subject = "New Booking Confirmation"
        message = f"Student {student_id} has booked a slot.\nDate: {date}\nTime: {time}\nSection: {section}"

        # Send email notification to admins
        send_email(admin_emails, subject, message)

        # Send confirmation to the student
        send_email([student_id], "Booking Confirmed", f"Dear {student_id},\nYour slot is confirmed on {date} at {time}.\nSection: {section}")

        # Fetch updated slots
        updated_slot_doc = bookings_collection.find_one({"section": section, "date": date})
        return jsonify({"message": "Slot successfully booked!", "slots": updated_slot_doc["slots"]}), 200
    else:
        return jsonify({"error": "Slot not available or already booked."}), 400



@app.route("/booked_slots/<section>/<date>", methods=["GET"])
def get_booked_slots(section, date):
    """Fetch booked slots with student IDs for a specific section and date."""
    slot_doc = bookings_collection.find_one({"section": section, "date": date})
    
    if not slot_doc:
        return jsonify({"error": "No slots found for the given section and date."}), 404

    # Filter to show only booked slots
    booked_slots = [
        {"time": slot["time"], "student_id": slot["student_id"]}
        for slot in slot_doc["slots"] if slot["booked"]
    ]

    return jsonify({"booked_slots": booked_slots}), 200

@app.route("/fully_booked_dates/<section>", methods=["GET"])
def get_fully_booked_dates(section):
    """Fetch fully booked dates for a section."""
    dates = bookings_collection.find({"section": section, "fully_booked": True}, {"date": 1})
    return jsonify({"fully_booked_dates": [doc["date"] for doc in dates]}), 200

@app.route("/delete_slot", methods=["POST"])
def delete_slot():
    data = request.json
    section = data["section"]
    date = format_date(data["date"])
    time = data["time"]

    result = bookings_collection.update_one(
        {"section": section, "date": date, "slots.time": time, "slots.booked": True},
        {"$set": {"slots.$.booked": False, "slots.$.student_id": None}}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Slot deleted successfully!"})
    return jsonify({"message": "Failed to delete slot. It might not be booked."}), 400

def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")


if __name__ == "__main__":
    app.run(debug=True)
