from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

app = Flask(__name__)
CORS(app)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client['CPR-Status']

@app.route('/students/<month>', methods=['GET'])
def get_students(month):
    students = list(db[month].find())
    return jsonify(dumps(students)), 200

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
    app.run(debug=True)