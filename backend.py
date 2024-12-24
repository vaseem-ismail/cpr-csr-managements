from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from pymongo import MongoClient
from flask_cors import CORS

# Initialize Flask app and extensions
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins
app.config['JWT_SECRET_KEY'] = '460680e7fe09d19e4063e23c51d3c53757920b054007273cd083703623c1cfea'  # Replace with your actual secret key
jwt = JWTManager(app)

# MongoDB setup (MongoDB Atlas)
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"  # Replace with your MongoDB URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['CPR-Details']
users_collection = db['users']

# User Registration (No Hashing)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Extract data from request
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    section = data.get('section')
    role = data.get('role')

    # Validation checks
    if not name or not email or not password or not section or not role:
        return jsonify({'error': 'All fields are required'}), 400

    # Check if email already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    # Insert user data into the database
    user_data = {
        'name': name,
        'email': email,
        'password': password,  # Note: Store hashed passwords in production!
        'section': section,
        'role': role
    }
    users_collection.insert_one(user_data)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json  # Parse incoming JSON
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user by email
        user = users_collection.find_one({'email': email})

        if user and user['password'] == password:
            return jsonify({
                'message': 'Login successful',
                'name': user['name'],
                'role': user['role'],
                'section': user['section']
            }), 200

        return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Password Reset (No Hashing)
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

    # Update the password (no hashing)
    users_collection.update_one({"email": email}, {"$set": {"password": new_password}})

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

    # Check if old password is correct (plain text comparison)
    if user['password'] != old_password:
        return jsonify({"error": "Incorrect old password"}), 401

    # Update the password (no hashing)
    users_collection.update_one({"email": email}, {"$set": {"password": new_password}})

    return jsonify({"message": "Password updated successfully"}), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
