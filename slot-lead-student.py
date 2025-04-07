from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil import parser
import traceback
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
calenderdb = client["Slot-Book"]
db = client['CPR-Status']
scoredb = client["Scores"]
invitedb = client['Slot_Booking']
sectiondb = client['CPR-Details']  
sections_collection = sectiondb["Users"]
track_db = client["track_goals"]
student_db = client['CPR-Details'] 
status_db = client['CPR-Status'] 
students_collection = student_db['Users']  

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "cpr.bot.ai@gmail.com"
EMAIL_PASSWORD = "hahk mply jiez tgja"

SectionA = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionB = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionC = ["mohamed.ismail@fssa.freshworks.com", "canvas9787839798@gmail.com"]

# showslot.html
# get-req.html

# Helper to serialize MongoDB ObjectId
def serialize_event(event):
    """Convert MongoDB ObjectId and datetime fields to strings."""
    event["_id"] = str(event["_id"])
    if "start_time" in event:
        event["start_time"] = event["start_time"].isoformat()
    if "end_time" in event:
        event["end_time"] = event["end_time"].isoformat()
    return event

# Helper to check if a collection exists
def section_exists(section):
    return section in calenderdb.list_collection_names()

# Get events for a specific section
@app.route("/get-events-<section>", methods=["GET"])
def get_events(section):
    try:
        if not section_exists(section):
            return jsonify({"error": f"Section '{section}' not found"}), 404
        
        events_collection = calenderdb[section]
        events = events_collection.find()
        print(events)
        return jsonify([serialize_event(event) for event in events]), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        
    
    
# Book a slot
@app.route('/book-slot-<section>/<date>', methods=['POST'])
def book_slot(section, date):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        print(data)
        slot = data.get("slot")
        admin_id = data.get("admin")
        student = data.get("student")

        if not date or not slot:
            return jsonify({"error": "Missing 'date' or 'slot' in request"}), 400
        print(data)

        # Validate date and time format
        # try:
        #     start_datetime = datetime.strptime(f"{date}", "%Y-%m-%d %H:%M")
        # except ValueError:
        #     return jsonify({"error": "Invalid 'date' or 'time' format"}), 400
        print(slot,admin_id,student,date)
        time = slot.replace("AM","")
        # end_datetime = start_datetime + timedelta(hours=1)
        print(time)

        event_data = {
            # "time": date,
            # "end_time": end_datetime,
            "date": date,
            "admin": data.get("admin"),
            "student": data.get("student"),
            "role": data.get("role"),
            "slot": slot,
            "section": section,
        }
        
            # Email recipient selection
        admin_emails = []
        if section == "A":
            admin_emails = SectionA
        elif section == "B":
            admin_emails = SectionB
        elif section == "C":
            admin_emails = SectionC
        # Email Content
        subject = "CPR Slot Booking Details - Admin"
        message = f"Your Coach {admin_id} has booked a slot with {student}.\nDate: {date}\nSection: {section}"
        
        send_email([student],subject,message)
        
        subject1 = "Booking Confirmed - CPR - AI"
        message1 = f"Dear {admin_emails} your CPR Booking with {student} is Booked and the email sent to {student}"
        
        send_email([admin_emails],subject1,message1)
        

        # Check for slot conflicts
        # conflict = calenderdb[section].find_one({
        #     "start_time": {"$lt": end_datetime},
        #     "end_time": {"$gt": start_datetime}
        # })

        # if conflict:
        #     return jsonify({"error": "Slot already booked for this time"}), 400
        print(event_data)

        # Insert the event into the section's collection
        calenderdb[section].insert_one(event_data)

        # Insert into student's collection
        student_name = data.get("student", "").replace(" ", "_")
        print(student_name)
        if student_name:
            student_collection = calenderdb.get_collection(student_name)
            student_collection.insert_one(event_data)

        return jsonify({"message": "Slot booked successfully"}), 201

    except Exception as e:
        app.logger.error(f"Error booking slot: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# Get details of a specific slot
@app.route("/slot-details/<section>/<date>", methods=["GET"])
def slot_details(section, date):
    try:
        if not section_exists(section):
            return jsonify({"error": f"Section '{section}' not found"}), 404

        try:
            slot = calenderdb[section].find_one({"date":date})
        except Exception as e:
            return jsonify({"error": "Invalid slot ID format"}), 400

        if not slot:
            return jsonify({"error": "Slot not found"}), 404

        return jsonify(serialize_event(slot)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Delete a specific slot
@app.route("/delete-slot/<section>/<slot>", methods=["DELETE"])
def delete_slot(section, slot):
    # slotfix = str(slot);
    # print(slotfix)
    try:
        # if not section_exists(section):
        #     return jsonify({"error": f"Section '{section}' not found"}), 404

        slotdet = calenderdb[section].find_one({"slot": slot})
        print(slotdet)
        if not slotdet:
            return jsonify({"error": f"Slot with ID '{slotdet}' not found"}), 404

        calenderdb[section].delete_one({"slot": slot})

        student_name = slotdet.get("student", "").replace(" ", "_")
        print(student_name)
        if student_name in calenderdb.list_collection_names():
            calenderdb[student_name].delete_one({"slot": slot})

        return jsonify({"message": "Slot deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Get slots for a specific student
@app.route('/student-slots/<string:student_name>', methods=['GET'])
def get_student_slots(student_name):
    try:
        formatted_name = student_name.replace(" ", "_")
        if not section_exists(formatted_name):
            return jsonify({"message": "No slots found for this student"}), 404

        student_collection = calenderdb[formatted_name]
        slots = list(student_collection.find())
        return jsonify([serialize_event(slot) for slot in slots]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)