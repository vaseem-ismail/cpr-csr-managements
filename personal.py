from flask import Flask,request,jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime,timezone
app = Flask(__name__)
CORS(app)

MONGO_URI = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
notes_admin_db = MONGO_URI["Notes-admin"]
notes_lead_db = MONGO_URI["Notes-lead"]


@app.route("/get-notes-admin-<name>",methods = ["POST"])
def get_admin_notes(name):
    data = request.get_json()
    Title = data.get("Title")
    #Topic =request.get_json()
    Notes = data.get("Notes")
    email = data.get("email")
    # Get current date and time separately
    date = datetime.now(timezone.utc).date().isoformat()  # "YYYY-MM-DD"
    time = datetime.now(timezone.utc).time().strftime("%H:%M:%S")  # "HH:MM:SS"
    
    if not email or not Notes or not Title:
        return jsonify({"error":"email or Notes are not defined properly, Please Check and try again"}),404
    notes_collection_admin = notes_admin_db[Title]
    print(notes_collection_admin)
    insert = notes_collection_admin.insert_one({"Topic":Title,"name":name,"date":date,"time":time,"email":email,"Title":Title,"Notes":Notes})
    
    if(insert):
        return jsonify({"message":"the data has been saved succesfully"}),201
    else:
        return jsonify({"error":"the data has not inserted on the database properly"}),404
    
    
@app.route("/get-all-notes-admin/<name>",methods = ["GET"])
def all_admin_notes(name):
    #data = request.get_json()
    notes_collection_admin = notes_admin_db[name]
    takedata = notes_collection_admin.find({},{"_id":0})
    print(takedata)
    takedata_list = list(takedata)
    if(takedata_list):
        return jsonify({"data":takedata_list}),200
    else:
        return jsonify({"error":"The data not got yet"})
    
    
    
@app.route("/get-notes-lead-<name>",methods = ["POST"])
def get_lead_notes(name):
    data = request.get_json()
    Title = data.get("topic")
    #Topic =request.get_json()
    Notes = data.get("Notes")
    email = data.get("email")
    # Get current date and time separately
    date = datetime.now(timezone.utc).date().isoformat()  # "YYYY-MM-DD"
    time = datetime.now(timezone.utc).time().strftime("%H:%M:%S")  # "HH:MM:SS"
    
    if not email or not Notes or not Title :
        return jsonify({"error":"email or Notes are not defined properly, Please Check and try again"}),404
    notes_lead_admin = notes_admin_db[name]
    print(notes_lead_admin)
    insert = notes_lead_admin.insert_one({"name":name,"date":date,"time":time,"email":email,"Notes":Notes,"Title":Title})
    
    if(insert):
        return jsonify({"message":"the data has been saved succesfully"}),201
    else:
        return jsonify({"error":"the data has not inserted on the database properly"}),404
    
    
@app.route("/get-all-notes-lead/<name>",methods = ["GET"])
def all_lead_notes(name):
    #data = request.get_json()
    notes_lead_admin = notes_lead_db[name]
    takedata = notes_lead_admin.find({},{"_id":0})
    print(takedata)
    takedata_list = list(takedata)
    if(takedata_list):
        return jsonify({"data":takedata_list}),200
    else:
        return jsonify({"error":"The data not got yet"})
    

    

if __name__ == "__main__":
    app.run(debug = True, port=5002)