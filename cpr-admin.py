from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil import parser
import traceback
import smtplib
from email.mime.text import MIMEText

client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client['CPR-Status']

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# ro.html 
# finished

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


if __name__ == "__main__":
    app.run(debug=True)
