from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from database.connection import db
import shutil
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import face_recognition

router = APIRouter()
UPLOAD_DIR = "dataset/"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure dataset directory exists

# Load known faces once at startup
known_face_encodings = []
known_emp_ids = []
recent_attendance = {}  # Dictionary to store last attendance time for each emp_id
ATTENDANCE_THRESHOLD = timedelta(minutes=5)  # Prevent duplicate attendance within 5 minutes

def load_known_faces():
    global known_face_encodings, known_emp_ids
    known_face_encodings.clear()
    known_emp_ids.clear()
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith(".jpg"):
                image_path = os.path.join(UPLOAD_DIR, filename)
                img = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(img)
                if encoding:
                    known_face_encodings.append(encoding[0])
                    known_emp_ids.append(filename.split(".")[0])
    except Exception as e:
        print(f"Error loading known faces: {str(e)}")

# Load known faces initially
load_known_faces()

@router.post("/add-user")
async def add_user(
    emp_id: str = Form(...),
    name: str = Form(...),
    role: str = Form(...),
    department: str = Form("Not Specified"),
    photo: UploadFile = File(...)
):
    """API to add a new user with a photo"""
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{emp_id}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        user = {
            "emp_id": emp_id,
            "name": name,
            "role": role,
            "department": department,
            "photo": file_path,
        }
        await db.users.insert_one(user)  # Save in MongoDB
        load_known_faces()  # Reload known faces after adding a new user

        return {"message": "User added successfully", "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}

def recognize_face(frame):
    """Recognize face from camera frame and match with stored images"""
    emp_id = "Unknown"
    try:
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            if known_face_encodings:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.5:
                    emp_id = known_emp_ids[best_match_index]
                    break  # Stop checking once a match is found
    except Exception as e:
        print(f"Face Recognition Error: {str(e)}")
    
    return frame, emp_id

@router.post("/api/mark-attendance")
async def mark_attendance(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        _, emp_id = recognize_face(frame)
        if emp_id != "Unknown":
            now = datetime.now()
            
            # Check if attendance was recently marked
            if emp_id in recent_attendance:
                last_marked_time = recent_attendance[emp_id]
                if now - last_marked_time < ATTENDANCE_THRESHOLD:
                    return JSONResponse(content={"message": f"Attendance already marked for {emp_id}"})
            
            recent_attendance[emp_id] = now  # Update last marked time
            attendance_entry = {
                "emp_id": emp_id,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            }
            await db.attendance.insert_one(attendance_entry)
            return JSONResponse(content={"message": f"Attendance marked for {emp_id}", "timestamp": attendance_entry["timestamp"]})
        
        return JSONResponse(content={"message": "No face recognized"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
