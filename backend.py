from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from flask_cors import CORS
import re

# Initialize Flask app and extensions
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = '460680e7fe09d19e4063e23c51d3c53757920b054007273cd083703623c1cfea'  # Replace with your actual secret key
jwt = JWTManager(app)

# MongoDB setup (MongoDB Atlas)
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"  # Replace with your MongoDB URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['sample_mflix']
users_collection = db['users']

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    # Check if email already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert new user into database
    users_collection.insert_one({'name': name, 'email': email, 'password': hashed_password})

    return jsonify({'message': 'User registered successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})
    if user:
        # Compare hashed password
        if bcrypt.check_password_hash(user['password'], password):
            return jsonify({
                "message": "Login successful",
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],  # Add a role field if needed
            }), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    else:
        return jsonify({"error": "User not found"}), 404

# Password Reset
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({'error': 'Email and new password are required'}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update the password
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

    return jsonify({"message": "Password reset successful"}), 200

# Profile Update (change password from profile)
@app.route('/update-password', methods=['PUT'])
@jwt_required()  # Ensure the user is logged in
def update_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not email or not old_password or not new_password:
        return jsonify({'error': 'Email, old password, and new password are required'}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if old password is correct
    if not bcrypt.check_password_hash(user['password'], old_password):
        return jsonify({"error": "Incorrect old password"}), 401

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update the password
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

    return jsonify({"message": "Password updated successfully"}), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
