from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from dateutil import parser
import datetime

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"
DB_NAME = "Slot-Book"
client = MongoClient(MONGO_URI)
calenderdb = client[DB_NAME]

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
    required_fields = ["date", "admin", "student", "role", "section"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Invalid event data, required fields are missing"}), 400

    try:
        # Parse date
        date_obj = parser.parse(data["date"])
    except ValueError:
        return jsonify({"error": "Invalid datetime format, use a proper format"}), 400

    try:
        event_data = {
            "start_time": date_obj,
            "end_time": date_obj + datetime.timedelta(hours=1),
            "admin": data["admin"],
            "student": data["student"],
            "role": data["role"],
            "section": data["section"]
        }

        # Check if slot already exists
        existing_event = calenderdb[section].find_one({
            "start_time": {"$lt": date_obj + datetime.timedelta(hours=1)},
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

if __name__ == "__main__":
    app.run(debug=True)
