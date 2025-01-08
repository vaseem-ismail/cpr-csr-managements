from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import calendar
from flask_cors import CORS

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes and origins

# MongoDB connection
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"
DB_NAME = "CPR-Details"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
sections_collection = db["Users"]



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


if __name__ == '__main__':
    app.run(debug=True)
