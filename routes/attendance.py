from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from database.connection import db
import shutil
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import face_recognition
from bson import ObjectId
from fastapi import APIRouter, Query
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

# List of connected WebSocket clients
connected_clients = set()

UPLOAD_DIR = "dataset/"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure dataset directory exists

# Load known faces once at startup
known_face_encodings = []
known_emp_ids = []
recent_attendance = {}  # Dictionary to store last attendance time for each emp_id
ATTENDANCE_THRESHOLD = timedelta(minutes=5)  # Prevent duplicate attendance within 5 minutes
OFFICE_START_TIME = datetime.strptime("09:00", "%H:%M").time()
LATE_ATTENDANCE_TIME = datetime.strptime("09:15", "%H:%M").time()

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

async def notify_clients(attendance_entry):
    for client in connected_clients:
        await client.send_text(json.dumps({"new_attendance": attendance_entry}))

@router.post("/mark-attendance")
async def mark_attendance(file: UploadFile = File(...), websocket: WebSocket = None):
    try:
        image_bytes = await file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        _, emp_id = recognize_face(frame)
        if emp_id != "Unknown":
            now = datetime.now()
            if emp_id in recent_attendance and now - recent_attendance[emp_id] < ATTENDANCE_THRESHOLD:
                return JSONResponse(content={"message": f"Attendance already marked for {emp_id}"})

            recent_attendance[emp_id] = now  # Update last marked time
            attendance_status = "On-time" if now.time() <= LATE_ATTENDANCE_TIME else "Late"
            
            user = await db.users.find_one({"emp_id": emp_id})
            emp_name = user["name"] if user else "Unknown"

            attendance_entry = {
                "emp_id": emp_id,
                "emp_name": emp_name,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "status": attendance_status
            }
            await db.attendance_collection.insert_one(attendance_entry)

            # **Send data to all WebSocket clients**
            await notify_clients(attendance_entry)

            return JSONResponse(content={"message": f"Attendance marked for {emp_name} ({emp_id})", "timestamp": attendance_entry["timestamp"], "status": attendance_status})

        return JSONResponse(content={"message": "No face recognized"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@router.get("/get-attendance")
async def get_attendance():
    try:
        records = await db.attendance_collection.find().to_list(None)  # ✅ Corrected Collection Name

        # Convert ObjectId and datetime fields to string
        for record in records:
            record["_id"] = str(record["_id"])
            if "timestamp" in record and isinstance(record["timestamp"], datetime):
                record["timestamp"] = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return JSONResponse(content={"attendance": records})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
    
@router.post("/add-attendance")
async def add_attendance(data: dict):
    try:
        # Insert into database
        new_record = await db.attendance_collection.insert_one(data)
        data["_id"] = str(new_record.inserted_id)

        # Broadcast update to WebSocket clients
        for client in connected_clients:
            await client.send_text(json.dumps({"new_attendance": data}))

        return {"message": "Attendance added successfully", "record": data}
    except Exception as e:
        return {"error": str(e)}
    
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

        
@router.get("/get-weekly-attendance")
async def get_weekly_attendance(emp_id: str = Query(...)):
    try:
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())  

        # ✅ Convert stored timestamps from string to datetime before filtering
        records = await db.attendance_collection.find({
            "emp_id": emp_id
        }).to_list(None)

        filtered_records = []
        for record in records:
            if "timestamp" in record:
                if isinstance(record["timestamp"], str):  
                    record["timestamp"] = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")

                if record["timestamp"] >= week_start:  
                    record["_id"] = str(record["_id"])
                    record["timestamp"] = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                    filtered_records.append(record)

        return JSONResponse(content={"weekly_attendance": filtered_records})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

@router.get("/get-monthly-attendance")
async def get_monthly_attendance(
    emp_id: str = Query(...), 
    month: int = Query(datetime.utcnow().month), 
    year: int = Query(datetime.utcnow().year)
):
    try:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        print(f"Checking attendance for emp_id: {emp_id}, Month: {month}, Year: {year}")  # Debugging

        records = await db.attendance_collection.find({
            "emp_id": emp_id,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }).to_list(None)

        if not records:
            print("No records found!")  # Debugging

        for record in records:
            record["_id"] = str(record["_id"])
            if "timestamp" in record and isinstance(record["timestamp"], datetime):
                record["timestamp"] = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return JSONResponse(content={"monthly_attendance": records})
    except Exception as e:
        print("Error:", str(e))  # Debugging
        return JSONResponse(content={"error": str(e)})

@router.get("/get-yearly-attendance")
async def get_yearly_attendance(
    emp_id: str = Query(...), 
    year: int = Query(datetime.utcnow().year)
):
    try:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        print(f"Checking attendance for emp_id: {emp_id}, Year: {year}")  # Debugging

        records = await db.attendance_collection.find({
            "emp_id": emp_id,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }).to_list(None)

        if not records:
            print("No records found!")  # Debugging

        for record in records:
            record["_id"] = str(record["_id"])
            if "timestamp" in record and isinstance(record["timestamp"], datetime):
                record["timestamp"] = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return JSONResponse(content={"yearly_attendance": records})
    except Exception as e:
        print("Error:", str(e))  # Debugging
        return JSONResponse(content={"error": str(e)})