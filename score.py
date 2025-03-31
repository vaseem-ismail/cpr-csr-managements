from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
scoredb = client["Scores"]

# score1.html

#Admin Score update for Students
# Admin adds scores for a student
@app.route('/add_scores', methods=['POST'])
def add_scores():
    data = request.json
    section = data.get('section')
    email = data.get('email')
    scores = data.get('scores')

    if not section or not email or not scores or len(scores) != 6:
        return jsonify({"error": "Invalid input. Section, email, and 6 scores are required."}), 400

    # Get the current month
    current_month = datetime.utcnow().strftime("%B")

    collection = scoredb[f"Section_{section}"]
    student_data = {
        "email": email,
        "scores": scores,
        "month": current_month,  # Store the month
        "timestamp": datetime.utcnow()
    }
    collection.update_one({"email": email, "month": current_month}, {"$set": student_data}, upsert=True)
    return jsonify({"message": f"Scores added for {email} in section {section} for the month of {current_month}"}), 200

# Lead fetches all scores in a section
@app.route('/get_section_scores', methods=['GET'])
def get_section_scores():
    section = request.args.get('section')
    month = request.args.get('month')  # Optional parameter

    # Validate section input
    if section not in ['A', 'B', 'C']:
        return jsonify({"error": "Invalid section. Valid sections are A, B, and C."}), 400

    collection = scoredb[f"Section_{section}"]
    query = {}
    if month:
        query["month"] = month  # Filter by month if provided

    scores = list(collection.find(query, {"_id": 0}))  # Fetch scores based on the query
    if scores:
        return jsonify({"scores": scores}), 200
    return jsonify({"message": "No scores found for the specified criteria"}), 200


# Student fetches their own scores
@app.route('/get_student_scores', methods=['GET'])
def get_student_scores():
    email = request.args.get('email')
    section = request.args.get('section')
    month = request.args.get('month')

    if not email or not section or not month:
        return jsonify({"error": "Email and section and month are required"}), 400
    
    print(email,month,section)

    collection = scoredb[f"Section_{section}"]
    student_scores = collection.find_one({"email": email,"month":month}, {"_id": 0, "scores": 1})
    if student_scores:
        return jsonify({"scores": student_scores["scores"]}), 200

    return jsonify({"message": "Scores not available"}), 200

@app.route('/get_scores_by_month', methods=['GET'])
def get_scores_by_month():
    section = request.args.get('section')  
    month = request.args.get('month')  

    if not section or not month:
        return jsonify({"error": "Section and month are required."}), 400

    # Fetch scores from the respective collection based on section and month
    collection = scoredb[f"Section_{section}"]
    scores = list(collection.find({"month": month}, {"_id": 0}))  # Exclude `_id` for cleaner output

    if not scores:
        return jsonify({"message": f"No scores found for section {section} in {month}"}), 404

    return jsonify({"scores": scores}), 200


if __name__ == "__main__":
    app.run(debug=True,port=5001)
