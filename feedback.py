from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app) 

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client["CPR-Details"]  
sectiondb = client['CPR-Details']  
sections_collection = sectiondb["Users"]

# dis&feed.html
# feedback.html
# dcfb.html


#FeedBack System
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

        # Sanitize collection names
        sender_collection_name = sender_email.replace('.', '_').replace('@', '_')
        receiver_collection_name = receiver_email.replace('.', '_').replace('@', '_')

        # Dynamically create or use collections for both sender and receiver
        sender_collection = db[sender_collection_name]
        receiver_collection = db[receiver_collection_name]

        # Create a feedback document
        feedback_document = {
            "from": sender_email,
            "to": receiver_email,
            "textcontent": feedback_message,
            "timestamp": datetime.utcnow()
        }

        # Insert the feedback document into both collections
        sender_collection.insert_one(feedback_document)
        receiver_collection.insert_one(feedback_document)

        return jsonify({"message": f"Feedback stored in '{sender_email}' and '{receiver_email}' collections"}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An internal error occurred"}), 500



@app.route('/get-feedback/<sender_email>', methods=['GET'])
def get_feedback(sender_email):
    try:
        # Sanitize the sender's email for collection name
        collection_name = sender_email.replace('.', '_').replace('@', '_')

        # Check if the collection exists
        if collection_name not in db.list_collection_names():
            return jsonify({"error": "No feedback found for the given email"}), 404

        # Retrieve all feedback documents from the collection
        feedback_collection = db[collection_name]
        feedbacks = list(feedback_collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id field from the result

        return jsonify({"feedbacks": feedbacks}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
    
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
        if collection_name not in sectiondb.list_collection_names():
            return jsonify({"error": f"No feedback found for {email}"}), 404

        # Retrieve feedback documents from the collection
        feedback_collection = sectiondb[collection_name]
        feedbacks = list(feedback_collection.find({}, {"_id": 0}))

        return jsonify({"feedbacks": feedbacks}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == "__main__":
    app.run(debug=True)
