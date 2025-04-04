from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
student_db = client['CPR-Details'] 
status_db = client['CPR-Status']
students_collection = student_db['Users']


#leads/status.html


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


if __name__ == "__main__":
    app.run