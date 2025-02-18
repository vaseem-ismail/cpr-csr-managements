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
# Databases
student_db = client['CPR-Details'] 
status_db = client['CPR-Status'] 

# Collections
students_collection = student_db['Users']  


# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"  # Change to your SMTP provider
SMTP_PORT = 587
EMAIL_SENDER = "cpr.bot.ai@gmail.com"
EMAIL_PASSWORD = "hahk mply jiez tgja"  # Use environment variables for security

SectionA = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionB = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionC = ["mohamed.ismail@fssa.freshworks.com", "canvas9787839798@gmail.com"]


#lead.html
#cpr-status.html
#score1.html
#get-invite.html
#calender.html




#Student CPR finshed Update 
#Student database Status Fetching
@app.route('/api/students', methods=['GET'])
def fetch_students():
    section = request.args.get('section')  # Get section from query params
    month = request.args.get('month')  # Get month for status
    if not section or not month:
        return jsonify({"error": "Section and month are required"}), 400

    # Query the students collection to fetch students from the specified section
    students = students_collection.find({"section": section, "role": "Student"})

    # Access the corresponding month's collection for status in the status_db
    month_collection = status_db[month]  # Use the month name as the collection name
    status_data = {str(student['_id']): student['status'] for student in month_collection.find()}

    # Prepare the result by adding the status from the month collection
    students_list = []
    for student in students:
        student_status = status_data.get(str(student['_id']), "Not Complete")
        students_list.append({
            "name": student["name"].strip(),
            "email": student["email"].strip(),
            "status": student_status
        })

    return jsonify(students_list)

@app.route('/api/update_status', methods=['POST'])
def update_student_status():
    data = request.json
    section = data.get('section')
    month = data.get('month')
    status_updates = data.get('status_updates')  # List of student _ids and their status

    if not section or not month or not status_updates:
        return jsonify({"error": "Section, month, and status updates are required"}), 400

    # Access the corresponding month collection in the status database
    month_collection = status_db[month]

    # Check if the collection exists, if not, create it
    if month not in status_db.list_collection_names():
        status_db.create_collection(month)

    # Update the status for each student in the list
    for update in status_updates:
        student_id = update.get('student_id')
        status = update.get('status')
        if student_id and status:
            # Update or insert the student's status in the specific month collection
            month_collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {"status": status}},
                upsert=True  # Create a new record if it doesn't exist
            )

    return jsonify({"message": "Status updated successfully"}), 200



def serialize_student(student):
    """
    Converts MongoDB document to a JSON serializable format,
    especially for the _id field.
    """
    student['_id'] = str(student['_id'])  # Convert ObjectId to string
    return student


@app.route('/students/<month>', methods=['GET'])
def fetch_students_by_month(month):
    section = request.args.get('section')  # Get 'section' from query parameters
    if section:
        # Fetch students and preserve insertion order (or any other desired order)
        students = list(db[month].find({"section": section}).sort("name", 1))  # Sort by insertion order (_id)
    else:
        students = list(db[month].find().sort("_id", 1))  # Sort by insertion order

    # Serialize each student to make the _id field JSON serializable
    serialized_students = [serialize_student(student) for student in students]
    
    return jsonify(serialized_students), 200


# @app.route('/students/<month>', methods=['GET'])
# def fetch_students_by_month(month):
#     section = request.args.get('section')  # Get 'section' from query parameters
#     if section:
#         students = list(db[month].find({"section": section}))  # Filter by section
#     else:
#         students = list(db[month].find())  # Return all students if no section is provided

#     # Serialize each student to make the _id field JSON serializable
#     serialized_students = [serialize_student(student) for student in students]
    
#     return jsonify(serialized_students), 200

@app.route('/students/<month>/update', methods=['POST'])
def update_monthly_status(month):
    data = request.json
    student_id = data.get('_id')
    new_status = data.get('status')

    result = db[month].update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"status": new_status}}
    )
    return jsonify({"modified_count": result.modified_count}), 200


#Admin Score update for Students
# Admin adds scores for a student
@app.route('/add_scores', methods=['POST'])
def add_scores():
    data = request.json
    section = data.get('section')
    email = data.get('email')
    scores = data.get('scores')

    if not section or not email or not scores or len(scores) != 6:
        return jsonify({"error": "Invalid input. Section, email, and 6 scores are required."}), 400

    # Get the current month
    current_month = datetime.utcnow().strftime("%B")

    collection = scoredb[f"Section_{section}"]
    student_data = {
        "email": email,
        "scores": scores,
        "month": current_month,  # Store the month
        "timestamp": datetime.utcnow()
    }
    collection.update_one({"email": email, "month": current_month}, {"$set": student_data}, upsert=True)
    return jsonify({"message": f"Scores added for {email} in section {section} for the month of {current_month}"}), 200

# Lead fetches all scores in a section
@app.route('/get_section_scores', methods=['GET'])
def get_section_scores():
    section = request.args.get('section')
    month = request.args.get('month')  # Optional parameter

    # Validate section input
    if section not in ['A', 'B', 'C']:
        return jsonify({"error": "Invalid section. Valid sections are A, B, and C."}), 400

    collection = scoredb[f"Section_{section}"]
    query = {}
    if month:
        query["month"] = month  # Filter by month if provided

    scores = list(collection.find(query, {"_id": 0}))  # Fetch scores based on the query
    if scores:
        return jsonify({"scores": scores}), 200
    return jsonify({"message": "No scores found for the specified criteria"}), 200


# Student fetches their own scores
@app.route('/get_student_scores', methods=['GET'])
def get_student_scores():
    email = request.args.get('email')
    section = request.args.get('section')
    month = request.args.get('month')

    if not email or not section or not month:
        return jsonify({"error": "Email and section and month are required"}), 400
    
    print(email,month,section)

    collection = scoredb[f"Section_{section}"]
    student_scores = collection.find_one({"email": email,"month":month}, {"_id": 0, "scores": 1})
    if student_scores:
        return jsonify({"scores": student_scores["scores"]}), 200

    return jsonify({"message": "Scores not available"}), 200

@app.route('/get_scores_by_month', methods=['GET'])
def get_scores_by_month():
    section = request.args.get('section')  # Get the section (specific to the coach)
    month = request.args.get('month')  # Get the selected month

    if not section or not month:
        return jsonify({"error": "Section and month are required."}), 400

    # Fetch scores from the respective collection based on section and month
    collection = scoredb[f"Section_{section}"]
    scores = list(collection.find({"month": month}, {"_id": 0}))  # Exclude `_id` for cleaner output

    if not scores:
        return jsonify({"message": f"No scores found for section {section} in {month}"}), 404

    return jsonify({"scores": scores}), 200

@app.route('/fetch-cpr-invitations', methods=['GET'])
def fetch_cpr_invitations():
    student_name = request.args.get('student')
    student_section = request.args.get('section')

    if not student_name or not student_section:
        return jsonify({"success": False, "message": "Missing student name or section."}), 400

    try:
        # Use student name to determine the collection name
        collection_name = student_name.replace(" ", "_")
        student_collection = invitedb[collection_name]

        # Query the database for invitations
        query = {"section": student_section}
        invitations = list(student_collection.find(query, {"_id": 0}))  # Exclude _id from response

        if invitations:
            return jsonify({"success": True, "invitations": invitations}), 200
        else:
            return jsonify({"success": True, "invitations": []}), 200
    except Exception as e:
        print(f"Error fetching CPR invitations: {e}")
        return jsonify({"success": False, "message": "Internal server error."}), 500
    
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
@app.route('/book-slot-<section>/<date>', methods=['POST', 'OPTIONS'])
def book_slot(section,date):
    if request.method == 'OPTIONS':
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        print(data)
        # date_str = data.get("date")
        slot = data.get("slot")
        # time_str = data.get("")
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
        return jsonify({"error": "An error occurred while booking the slot"}), 500

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

# Error Handlers
@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route('/get-students/<section>', methods=['GET'])
def get_students(section):
    """
    Fetch a list of students' emails for a given section.
    """
    try:
        # Query the database to fetch students in the given section
        # students_collection = db["students"]  # Assuming a "students" collection
        
        students = list(sections_collection.find({"section": section}, {"_id": 0, "email": 1}))

        # Extract only emails
        emails = [student["email"] for student in students]
        if not emails:
            return jsonify({"error": f"No students found in section {section}"}), 404

        return jsonify({"emails": emails}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get-feedback/<email>', methods=['GET'])
def get_feedback_by_email(email):
    """
    Fetch feedback for a given student's email.
    """
    try:
        # Sanitize the email to get the collection name
        collection_name = email.replace('.', '_').replace('@', '_')

        # Check if the collection exists
        if collection_name not in sectiondb.list_collection_names():
            return jsonify({"error": f"No feedback found for {email}"}), 404

        # Retrieve feedback documents from the collection
        feedback_collection = sectiondb[collection_name]
        feedbacks = list(feedback_collection.find({}, {"_id": 0}))

        return jsonify({"feedbacks": feedbacks}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/add-goals', methods=['POST'])
def add_multiple_goals():
    """
    Admin adds a single message containing goals for multiple subjects for a specific student.
    """
    data = request.json
    print(data)
    section = data.get('section')
    student_name = data.get('to')
    admin_name = data.get('from', 'Admin')  # Default sender is Admin
    goals = data.get('goals', [])  # List of goals for subjects
    month = data.get('month', datetime.now().strftime("%Y-%m"))  # Use selected month or default to current
    

    if not section or not student_name or not goals:
        return jsonify({"error": "Section, student name, and goals are required"}), 400

    collection_name = f"track_goals_{section}"
    collection = track_db[collection_name]

    message = {
        "from": admin_name,
        "to": student_name,
        "month": month,
        "goals": goals,  # Store all subject goals in one entry
    }

    collection.insert_one(message)

    return jsonify({"message": "Goals added successfully"}), 201



@app.route('/student-goals', methods=['GET'])
def get_student_goals():
    """
    Fetch all goals for a specific student by name, section, and month.
    """
    student_name = request.args.get('name')
    section = request.args.get('section')
    month = request.args.get('month')  # Get the selected month

    if not student_name or not section or not month:
        return jsonify({"error": "Student name, section, and month are required"}), 400

    collection_name = f"track_goals_{section}"
    collection = track_db[collection_name]

    goals = collection.find(
        {"to": student_name, "month": month},
        {"_id": 0, "from": 1, "to": 1, "goals": 1}
    )

    return jsonify({"goals": list(goals)})

if __name__ == '__main__':
    app.run(debug=True)
