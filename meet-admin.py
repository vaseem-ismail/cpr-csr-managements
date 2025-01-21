from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["slot_management"]
slots_collection = db["slots"]

# Get calendar for a section
@app.route("/calendar/<section>", methods=["GET"])
def get_calendar(section):
    calendar = []
    today = datetime.now()

    # Start and end of the current month
    start_of_month = today.replace(day=1)
    next_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
    end_of_month = (next_month - timedelta(days=1)).date()

    current_day = start_of_month.date()

    while current_day <= end_of_month:
        date_str = current_day.strftime("%Y-%m-%d")
        slot_doc = slots_collection.find_one({"section": section, "date": date_str})
        if not slot_doc:
            default_slots = [{"time": f"{hour}:00", "booked": False} for hour in range(9, 17)]
            slots_collection.insert_one({
                "section": section,
                "date": date_str,
                "slots": default_slots
            })

        slot_doc = slots_collection.find_one({"section": section, "date": date_str})
        fully_booked = all(slot["booked"] for slot in slot_doc["slots"]) if slot_doc else False
        calendar.append({"date": date_str, "fully_booked": fully_booked})
        current_day += timedelta(days=1)

    return jsonify({"calendar": calendar}), 200


# Delete a slot
@app.route("/slot/<section>/<date>/<time>", methods=["DELETE"])
def delete_slot(section, date, time):
    result = slots_collection.update_one(
        {"section": section, "date": date},
        {"$pull": {"slots": {"time": time}}}
    )
    if result.modified_count > 0:
        return jsonify({"message": "Slot deleted successfully"}), 200
    else:
        return jsonify({"error": "Slot not found"}), 404


# Add a slot
@app.route("/slot/<section>/<date>", methods=["POST"])
def add_slot(section, date):
    data = request.json
    new_slot = {"time": data["time"], "booked": False}

    result = slots_collection.update_one(
        {"section": section, "date": date},
        {"$push": {"slots": new_slot}}
    )
    if result.modified_count > 0:
        return jsonify({"message": "Slot added successfully"}), 200
    else:
        return jsonify({"error": "Failed to add slot"}), 400


# Book a slot
@app.route("/book/<section>/<date>/<time>", methods=["POST"])
def book_slot(section, date, time):
    result = slots_collection.update_one(
        {"section": section, "date": date, "slots.time": time},
        {"$set": {"slots.$.booked": True}}
    )
    if result.modified_count > 0:
        return jsonify({"message": "Slot booked successfully"}), 200
    else:
        return jsonify({"error": "Failed to book slot"}), 400


if __name__ == "__main__":
    app.run(debug=True)
