from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime

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

    # Save the user details with plain-text password (not recommended for production)
    user_id = users_collection.insert_one({
        'name': name,
        'email': email,
        'password': password,
        'section': section,
        'role': role
    }).inserted_id

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = users_collection.find_one({'email': email})
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate a JWT token
    token = create_access_token(identity=str(user['_id']))
    return jsonify({'message': 'Login successful', 'token': token}), 200


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

# Send Feedback
@app.route('/send-feedback', methods=['POST'])
@jwt_required()
def send_feedback():
    data = request.get_json()
    from_email = data.get('from')
    to_email = data.get('to')  # Expecting an array of emails
    subject = data.get('subject')
    text_content = data.get('textcontent')

    if not from_email or not to_email or not subject or not text_content:
        return jsonify({'error': 'All fields are required'}), 400

    for recipient_email in to_email:
        # Dynamically create/access a collection named after the recipient email
        sanitized_collection_name = recipient_email.replace('.', '_').replace('@', '_')
        feedback_collection = db[sanitized_collection_name]

        # Insert feedback into the collection
        feedback_collection.insert_one({
            'from': from_email,
            'to': recipient_email,
            'subject': subject,
            'textcontent': text_content,
            'timestamp': datetime.utcnow()  # Add a timestamp for recordkeeping
        })

    return jsonify({'message': 'Feedback sent and stored successfully!'}), 200

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)

