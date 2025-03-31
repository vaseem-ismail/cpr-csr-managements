from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime
import re
import jwt

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# # Security configurations
# bcrypt = Bcrypt(app)
# app.config['JWT_SECRET_KEY'] = '460680e7fe09d19e4063e23c51d3c53757920b054007273cd083703623c1cfea'  # Replace with your secret key
# jwt = JWTManager(app)


secret_key = "CPRFSSAB4CSR"
algorithm = "HS256"


# MongoDB setup
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"  # Replace with your MongoDB Atlas connection string
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['CPR-Details']
users_collection = db['Users']

# login.html
# register.html
# change.html
# delete-user.html

@app.route('/register', methods=['POST'])   #checked register.html
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
    user_details = {
        'name': name,
        'email': email,
        'password': password,
        'section': section,
        'role': role
    }
    
    token = jwt.encode(user_details,secret_key,algorithm=algorithm)
     
    user_id = users_collection.insert_one({
        'token': token,
        'name': name,
        'email': email,
        'password': password,
        'section': section,
        'role': role
    }).inserted_id

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201

@app.route('/change-password', methods=['POST']) #checked change.html
def change_password():
    try:
        data = request.get_json()
        # email = data.get('email')
        token = data.get("token")
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not token or not current_password or not new_password:
            return jsonify({'error': 'Email, current password, and new password are required'}), 400

        # Fetch user by email
        user = users_collection.find_one({'token': token})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify current password
        if user['password'] != current_password: 
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Update the password in the database
        users_collection.update_one(
            {'token': token},
            {'$set': {'password': new_password}}
        )

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/login', methods=['POST']) # checked login.html
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
    
    return jsonify({
        # 'name': user['name'],
        # 'email': user['email'],
        # 'role': user['role'],
        # 'section': user['section'],
        'token': user['token']
    }), 200
    
@app.route('/delete_user', methods=['DELETE']) #checked delete-user.html
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


# Main entry point
if __name__ == '__main__':
    app.run(debug=True)

