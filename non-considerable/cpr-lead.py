from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil import parser
import traceback


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
    

# Error Handlers
@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500



    
if __name__ == '__main__':
    app.run(debug=True)
