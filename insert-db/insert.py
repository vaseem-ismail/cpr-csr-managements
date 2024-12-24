from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB setup
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"  # Replace with your MongoDB URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['CPR-Details']
users_collection = db['Users']

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

if __name__ == '__main__':
    app.run(debug=True)
