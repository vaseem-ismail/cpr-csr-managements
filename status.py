from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Allow CORS for all domains (you can specify the frontend URL if needed)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client['CPR-Status']

def serialize_student(student):
    """
    Converts MongoDB document to a JSON serializable format,
    especially for the _id field.
    """
    student['_id'] = str(student['_id'])  # Convert ObjectId to string
    return student

@app.route('/students/<month>', methods=['GET'])
def get_students(month):
    section = request.args.get('section')  # Get 'section' from query parameters
    if section:
        students = list(db[month].find({"section": section}))  # Filter by section
    else:
        students = list(db[month].find())  # Return all students if no section is provided

    # Serialize each student to make the _id field JSON serializable
    serialized_students = [serialize_student(student) for student in students]
    
    return jsonify(serialized_students), 200

@app.route('/students/<month>/update', methods=['POST'])
def update_status(month):
    data = request.json
    student_id = data.get('_id')
    new_status = data.get('status')

    result = db[month].update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"status": new_status}}
    )
    return jsonify({"modified_count": result.modified_count}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
