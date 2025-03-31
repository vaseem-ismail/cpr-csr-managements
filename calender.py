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

sectiondb = client['CPR-Details']  
sections_collection = sectiondb["Users"]
track_db = client["track_goals"] 
bookingdb = client["student_booking"] 
bookings_collection = bookingdb["bookings"]




SMTP_SERVER = "smtp.gmail.com"  # Change to your SMTP provider
SMTP_PORT = 587
EMAIL_SENDER = "cpr.bot.ai@gmail.com"
EMAIL_PASSWORD = "hahk mply jiez tgja"  # Use environment variables for security

SectionA = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionB = ["canvas9787839798@gmail.com", "canvas9787839798@gmail.com"]
SectionC = ["mohamed.ismail@fssa.freshworks.com", "canvas9787839798@gmail.com"]


# bookcpr.html





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

# @app.route('/get-feedback/<email>', methods=['GET'])
# def get_feedback_by_email(email):
#     """
#     Fetch feedback for a given student's email.
#     """
#     try:
#         # Sanitize the email to get the collection name
#         collection_name = email.replace('.', '_').replace('@', '_')

#         # Check if the collection exists
#         if collection_name not in sectiondb.list_collection_names():
#             return jsonify({"error": f"No feedback found for {email}"}), 404

#         # Retrieve feedback documents from the collection
#         feedback_collection = sectiondb[collection_name]
#         feedbacks = list(feedback_collection.find({}, {"_id": 0}))

#         return jsonify({"feedbacks": feedbacks}), 200
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return jsonify({"error": str(e)}), 500
    
# @app.route('/add-goals', methods=['POST'])
# def add_multiple_goals():
#     """
#     Admin adds a single message containing goals for multiple subjects for a specific student.
#     """
#     data = request.json
#     print(data)
#     section = data.get('section')
#     student_name = data.get('to')
#     admin_name = data.get('from', 'Admin')  # Default sender is Admin
#     goals = data.get('goals', [])  # List of goals for subjects
#     month = data.get('month', datetime.now().strftime("%Y-%m"))  # Use selected month or default to current
    

#     if not section or not student_name or not goals:
#         return jsonify({"error": "Section, student name, and goals are required"}), 400

#     collection_name = f"track_goals_{section}"
#     collection = track_db[collection_name]

#     message = {
#         "from": admin_name,
#         "to": student_name,
#         "month": month,
#         "goals": goals,  # Store all subject goals in one entry
#     }

#     collection.insert_one(message)

#     return jsonify({"message": "Goals added successfully"}), 201



# @app.route('/student-goals', methods=['GET'])
# def get_student_goals():
#     """
#     Fetch all goals for a specific student by name, section, and month.
#     """
#     student_name = request.args.get('name')
#     section = request.args.get('section')
#     month = request.args.get('month')  # Get the selected month

#     if not student_name or not section or not month:
#         return jsonify({"error": "Student name, section, and month are required"}), 400

#     collection_name = f"track_goals_{section}"
#     collection = track_db[collection_name]

#     goals = collection.find(
#         {"to": student_name, "month": month},
#         {"_id": 0, "from": 1, "to": 1, "goals": 1}
#     )

#     return jsonify({"goals": list(goals)})






if __name__ == '__main__':
    app.run(debug=True)
