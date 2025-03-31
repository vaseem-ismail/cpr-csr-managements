from flask import Flask, jsonify, request
from flask_cors import CORS
from track_goals import track_db, app

CORS(app)

# track-goals-student.html

@app.route('/student-goals', methods=['GET'])
def get_student_goals():
    """
    Fetch all goals for a specific student by name, section, and month.
    """
    student_name = request.args.get('name')
    section = request.args.get('section')
    month = request.args.get('month')  # Get the selected month

    if not student_name or not section or not month:
        return jsonify({"error": "Student name, section, and month are required"}), 400

    collection_name = f"track_goals_{section}"
    collection = track_db[collection_name]

    goals = collection.find(
        {"to": student_name, "month": month},
        {"_id": 0, "from": 1, "to": 1, "goals": 1}
    )

    return jsonify({"goals": list(goals)})



if __name__ == "__main__":
    app.run(debug=True)