from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil import parser

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
calenderdb = client["Slot-Book"]
db = client['CPR-Status']
scoredb = client["Scores"]
invitedb = client['Slot_Booking']  # Replace with your database name
sectiondb = client['CPR-Details']  # Replace with your database name
sections_collection = sectiondb["Users"]
track_db = client["track_goals"]  # Database name

## MongoDB connection for both databases
#student_client = MongoClient('mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/')  # Student database
#status_client = MongoClient('mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/')  # Status database

# Databases
student_db = client['CPR-Details']  # Replace with your student database name
status_db = client['CPR-Status']  # Replace with your status database name

# Collections
students_collection = student_db['Users']  # Students collection


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
        students = list(db[month].find({"section": section}))  # Filter by section
    else:
        students = list(db[month].find())  # Return all students if no section is provided

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

    if not email or not section:
        return jsonify({"error": "Email and section are required"}), 400

    collection = scoredb[f"Section_{section}"]
    student_scores = collection.find_one({"email": email}, {"_id": 0, "scores": 1})
    if student_scores:
        return jsonify({"scores": student_scores["scores"]}), 200

    return jsonify({"message": "Scores not available"}), 200

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
    event["_id"] = str(event["_id"])
    return event

# Get events for a specific section
@app.route("/get-events-<section>", methods=["GET"])
def get_events(section):
    try:
        if section not in calenderdb.list_collection_names():
            return jsonify([])  # Return an empty array for invalid sections
        events_collection = calenderdb[section]
        events = events_collection.find()
        return jsonify([serialize_event(event) for event in events])  # Always return an array
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Book a slot for a specific section
@app.route("/book-slot-<section>", methods=["POST"])
def book_slot(section):
    data = request.json
    required_fields = ["date", "time", "admin", "student", "role", "section"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Invalid event data, required fields are missing"}), 400

    try:
        # Parse date and time
        date_time_str = f"{data['date']} {data['time']}"
        date_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"error": "Invalid datetime format, use YYYY-MM-DD and HH:MM"}), 400

    try:
        event_data = {
            "start_time": date_obj,
            "end_time": date_obj + timedelta(hours=1),
            "admin": data["admin"],
            "student": data["student"],
            "role": data["role"],
            "section": data["section"]
        }

        # Check if slot already exists
        existing_event = calenderdb[section].find_one({
            "start_time": {"$lt": date_obj + timedelta(hours=1)},
            "end_time": {"$gt": date_obj}
        })
        if existing_event:
            return jsonify({"error": "Slot already booked"}), 400

        calenderdb[section].insert_one(event_data)
        return jsonify({"message": "Slot booked successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get details of a specific slot
@app.route("/slot-details/<section>/<slot_id>", methods=["GET"])
def slot_details(section, slot_id):
    try:
        if section not in calenderdb.list_collection_names():
            return jsonify({"error": "Invalid section"}), 404

        slot = calenderdb[section].find_one({"_id": ObjectId(slot_id)})
        if not slot:
            return jsonify({"error": "Slot not found"}), 404
        return jsonify(serialize_event(slot))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a specific slot
@app.route("/delete-slot/<section>/<slot_id>", methods=["DELETE"])
def delete_slot(section, slot_id):
    try:
        if section not in calenderdb.list_collection_names():
            return jsonify({"error": f"Invalid section: {section}"}), 404

        result = calenderdb[section].delete_one({"_id": ObjectId(slot_id)})
        if result.deleted_count == 0:
            return jsonify({"error": f"Slot with ID {slot_id} not found"}), 404
        return jsonify({"message": "Slot deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handling
@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "An internal server error occurred"}), 500


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
        if collection_name not in db.list_collection_names():
            return jsonify({"error": f"No feedback found for {email}"}), 404

        # Retrieve feedback documents from the collection
        feedback_collection = db[collection_name]
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
