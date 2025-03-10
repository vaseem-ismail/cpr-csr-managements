from pymongo import MongoClient
import secrets

CLIENT = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
Users_db = CLIENT["CPR-Details"]
Users_coll = Users_db["Users"]


def main():
    students = Users_coll.find({}, {"_id": 0}).to_list(length=None)
    print("Before Update:", students)

    for student in students:
        print("Processing Student:", student)

        if "name" not in student:
            print("No username found. Skipping:", student)
            continue  # Skip this document

        unique_token = secrets.token_hex(8)
        print(f"Updating {student['name']} with token {unique_token}")

        Users_coll.update_one(
            {"name": student["name"]},
            {"$set": {"token": unique_token}}
        )

    updated_students = Users_coll.find({}, {"_id": 0}).to_list(length=None)
    print("After Update:", updated_students)

    
if __name__ == "__main__":
    main()