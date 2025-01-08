from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"
client = MongoClient(MONGO_URI)
track_db = client["track_goals"]  # Database name

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

