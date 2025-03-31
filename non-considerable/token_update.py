from pymongo import MongoClient
import jwt

CLIENT = MongoClient("mongodb+srv://vaseemdrive01:mohamedvaseem@cprweb.6sp6c.mongodb.net/")
Users_db = CLIENT["CPR-Details"]
Users_coll = Users_db["Users"]


secret_key = "CPRFSSAB4CSR"
algorithm = "HS256"



def main():
    students = Users_coll.find({}, {"_id": 0,"token":0}).to_list(length=None)
    print("Before Update:", students)

    for student in students:
        print("Processing Student:", student)

        if "name" not in student:
            print("No username found. Skipping:", student)
            continue

        unique_token = jwt.encode(student, secret_key , algorithm= algorithm)
        print(f"Updating {student['name']} with token {unique_token}")

        Users_coll.update_one(
            {"name": student["name"]},
            {"$set": {"token": unique_token}}
        )

    updated_students = Users_coll.find({}, {"_id": 0}).to_list(length=None)
    print("After Update:", updated_students)

    
if __name__ == "__main__":
    main()