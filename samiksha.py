from flask import Flask,request,jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection    
MONGO_URI = "mongodb+srv://mohamedvaseem:mohamedvaseem@anime-galaxy.7lnts.mongodb.net/"
Mongo_client = MongoClient(MONGO_URI)
db = Mongo_client['Film-ki-Samiksha']
collection = db['wishlist']

@app.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    email = data.get('email')
    
     # Fetch the watch-later list
    watch_later_data = collection.find_one({'email': email})
    watch_later_list = watch_later_data['watchLaterList'] if watch_later_data else []
    
    return jsonify({
        "email": email,
        'watchLaterList': watch_later_list
    }), 200

# Store Watch Later list
@app.route('/storeWatchLater', methods=['POST'])
def store_watch_later():
    data = request.get_json()
    email = data.get('email')
    watch_later_list = data.get('watchLaterList')

    # Log received data for debugging
    print("Received data:", data)

    # Validate input
    if not email:
        print("Error: Email is required")
        return jsonify({'error': 'Email is required'}), 400
    if watch_later_list is None:
        print("Error: Watch Later list is required")
        return jsonify({'error': 'Watch Later list is required'}), 400
    if not isinstance(watch_later_list, list):
        print("Error: Watch Later list must be a list")
        return jsonify({'error': 'Watch Later list must be a list'}), 400

    # Update or create the watch-later list for the user
    result = collection.update_one(
        {'email': email},
        {'$set': {'watchLaterList': watch_later_list}},
        upsert=True
    )

    print("Update result:", result.raw_result)
    return jsonify({'message': 'Watch Later list updated successfully'}), 200



if __name__ == '__main__':
    app.run(debug=True)