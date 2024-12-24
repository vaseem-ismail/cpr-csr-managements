import pymongo
import bcrypt

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
db = client["sample_mflix"]
collection = db["users"]

# Function to verify password
def verify_password(username, password):
    user = collection.find_one({"username": username})
    if user:
        hashed_password = user["password"]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True
    return False

# Example usage
username = "Mohamed Vaseem Ismail"
password = "$2b$12$2Xprceza4mCBdzYnOOSwou3o0ZhxKGj.BIco7QuKwLM0E3DjydxPa"
user = collection.find_one({"username": username})
if user:
    hashed_password = user["password"]
    print(f"Username: {username}, Password: {password}")
else:
    print("User not found")
password = "example_password"
if verify_password(username, password):
    print("Password is correct")
else:
    print("Password is incorrect")