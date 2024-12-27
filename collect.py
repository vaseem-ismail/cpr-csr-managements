from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB setup
client = MongoClient('mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/')
db = client['CPR-Details']

@app.route('/get-feedbacks', methods=['POST'])
def get_feedbacks():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Convert email to collection name format
        collection_name = email.replace('@', '_').replace('.', '_')
        if collection_name not in db.list_collection_names():
            return jsonify({"error": f"No feedbacks found for {email}"}), 404

        feedback_collection = db[collection_name]
        feedbacks = list(feedback_collection.find({}, {'_id': 0}))  # Exclude `_id` field
        return jsonify(feedbacks), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
