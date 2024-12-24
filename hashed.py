from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Initialize MongoDB and Bcrypt
MONGO_URI = "mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['sample_mflix']
users_collection = db['users']
bcrypt = Bcrypt()

# Convert raw passwords to hashed passwords
def convert_passwords_to_hashed():
    users = users_collection.find()
    for user in users:
        if "password" in user and not user["password"].startswith("$2b$"):
            # Hash the raw password
            hashed_password = bcrypt.generate_password_hash(user["password"]).decode("utf-8")
            
            # Update the user document with the hashed password
            users_collection.update_one(
                {"_id": user["_id"]},  # Match by user ID
                {"$set": {"password": hashed_password}}
            )
            print(f"Password for user {user['email']} updated successfully.")

if __name__ == "__main__":
    convert_passwords_to_hashed()
