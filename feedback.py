from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Resource Sharing

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client["CPR-Details"]  # Replace with your database name

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        # Parse JSON from the request
        feedback_data = request.json

        # Extract fields from JSON
        sender_email = feedback_data.get('from')
        receiver_email = feedback_data.get('to')
        feedback_message = feedback_data.get('feedback')

        # Validate required fields
        if not sender_email or not receiver_email or not feedback_message:
            return jsonify({"error": "All fields (from, to, feedback) are required"}), 400

        # Dynamically create or use a collection named after the receiver's email
        collection_name = receiver_email.replace('.', '_').replace('@', '_')  # Sanitizing collection name
        feedback_collection = db[collection_name]

        # Create a feedback document
        feedback_document = {
            "from": sender_email,
            "to": receiver_email,
            "textcontent": feedback_message,
            "timestamp": datetime.utcnow()
        }

        # Insert the feedback document into the collection
        feedback_collection.insert_one(feedback_document)

        return jsonify({"message": f"Feedback stored in collection '{receiver_email}'"}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True)
