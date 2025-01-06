from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/Slot-Book?retryWrites=true&w=majority"
DB_NAME = "Slot-Book"
client = MongoClient(MONGO_URI)
calenderdb = client[DB_NAME]

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
        return jsonify([serialize_event(event) for event in events]), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Book a slot
@app.route('/book-slot-<section>', methods=['POST', 'OPTIONS'])
def book_slot(section):
    if request.method == 'OPTIONS':
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    try:
        date_str = data.get("date")
        time_str = data.get("time")

        if not date_str or not time_str:
            return jsonify({"error": "Missing 'date' or 'time' in request"}), 400

        # Validate date and time format
        try:
            start_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"error": "Invalid 'date' or 'time' format"}), 400

        end_datetime = start_datetime + timedelta(hours=1)

        event_data = {
            "start_time": start_datetime,
            "end_time": end_datetime,
            "admin": data.get("admin"),
            "student": data.get("student"),
            "role": data.get("role"),
            "section": section,
        }

        # Check for slot conflicts
        conflict = calenderdb[section].find_one({
            "start_time": {"$lt": end_datetime},
            "end_time": {"$gt": start_datetime}
        })

        if conflict:
            return jsonify({"error": "Slot already booked for this time"}), 400

        # Insert the event into the section's collection
        calenderdb[section].insert_one(event_data)

        # Insert into student's collection
        student_name = data.get("student", "").replace(" ", "_")
        if student_name:
            student_collection = calenderdb.get_collection(student_name)
            student_collection.insert_one(event_data)

        return jsonify({"message": "Slot booked successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get details of a specific slot
@app.route("/slot-details/<section>/<slot_id>", methods=["GET"])
def slot_details(section, slot_id):
    try:
        if not section_exists(section):
            return jsonify({"error": f"Section '{section}' not found"}), 404

        slot = calenderdb[section].find_one({"_id": ObjectId(slot_id)})
        if not slot:
            return jsonify({"error": "Slot not found"}), 404

        return jsonify(serialize_event(slot)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a specific slot
@app.route("/delete-slot/<section>/<slot_id>", methods=["DELETE"])
def delete_slot(section, slot_id):
    try:
        if not section_exists(section):
            return jsonify({"error": f"Section '{section}' not found"}), 404

        slot = calenderdb[section].find_one({"_id": ObjectId(slot_id)})
        if not slot:
            return jsonify({"error": f"Slot with ID '{slot_id}' not found"}), 404

        calenderdb[section].delete_one({"_id": ObjectId(slot_id)})

        student_name = slot.get("student", "").replace(" ", "_")
        if student_name in calenderdb.list_collection_names():
            calenderdb[student_name].delete_one({"_id": ObjectId(slot_id)})

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

if __name__ == "__main__":
    app.run(debug=True)
