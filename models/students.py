from pymongo import MongoClient
from bson.objectid import ObjectId

class StudentModel:
    def __init__(self, db):
        self.collection = db["students"]

    def add_student(self, name, student_id, face_encoding, department, year):
        student_data = {
            "name": name,
            "student_id": student_id,
            "face_encoding": face_encoding,
            "department": department,
            "year": year
        }
        return self.collection.insert_one(student_data)

    def get_student(self, student_id):
        return self.collection.find_one({"student_id": student_id})

    def get_all_students(self):
        return list(self.collection.find())

    def update_student(self, student_id, update_data):
        return self.collection.update_one({"student_id": student_id}, {"$set": update_data})

    def delete_student(self, student_id):
        return self.collection.delete_one({"student_id": student_id})
