from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        sender = data.get('sender_email')
        receiver = data.get('receiver_email')
        feedback = data.get('feedback')

        if not sender or not receiver or not feedback:
            return jsonify({"error": "All fields are required"}), 400

        collection_name = receiver
        receiver_collection = db[collection_name]

        feedback_document = {
            "sender": sender,
            "feedback": feedback,
            "timestamp": datetime.utcnow()
        }
        receiver_collection.insert_one(feedback_document)

        return jsonify({"message": "Feedback submitted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
