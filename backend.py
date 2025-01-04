from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime
import re

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Security configurations
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = '460680e7fe09d19e4063e23c51d3c53757920b054007273cd083703623c1cfea'  # Replace with your secret key
jwt = JWTManager(app)

# MongoDB setup
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"  # Replace with your MongoDB Atlas connection string
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['CPR-Details']
users_collection = db['Users']

#index.html
#from.html
#sent-fb.html
#feedback.html
#admin.html

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    section = data.get('section')
    role = data.get('role')

    if not email or not password or not name or not section or not role:
        return jsonify({'error': 'All fields are required'}), 400

    # Check if the user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400

    # Save the user details
    user_id = users_collection.insert_one({
        'name': name,
        'email': email,
        'password': password,
        'section': section,
        'role': role
    }).inserted_id

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201

@app.route('/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        email = data.get('email')
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not email or not current_password or not new_password:
            return jsonify({'error': 'Email, current password, and new password are required'}), 400

        # Fetch user by email
        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if user['password'] != current_password:  # No hashing as per your request
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Update the password in the database
        users_collection.update_one(
            {'email': email},
            {'$set': {'password': new_password}}
        )

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = users_collection.find_one({'email': email})
    if not user or user['password'] != password:  # No hashing as per your requirement
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate a JWT token
    token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'section': user['section']
    }), 200
    
@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Find and delete the user by email
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_collection.delete_one({'email': email})

    return jsonify({'message': 'User deleted successfully'}), 200




# Get User Details
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': user_id})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'email': user['email'],
        'message': 'User profile fetched successfully.'
    }), 200

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
    


# Main entry point
if __name__ == '__main__':
    app.run(debug=True)

