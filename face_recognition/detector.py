import cv2
import face_recognition
import numpy as np
from database.connection import db

async def recognize_face(frame):
    """Detect and recognize faces in a frame"""
    known_faces = []
    known_ids = []

    try:
        users = await db.users.find().to_list(100)  # Get all stored users
        for user in users:
            img = face_recognition.load_image_file(user["photo"])
            encoding = face_recognition.face_encodings(img)

            if encoding:
                known_faces.append(encoding[0])
                known_ids.append(user["emp_id"])

        # Convert frame for processing (Resize first to speed up)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Reduce frame size
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, location in zip(face_encodings, face_locations):
            name = "Unknown"

            if known_faces:
                face_distances = face_recognition.face_distance(known_faces, face_encoding)
                best_match_index = np.argmin(face_distances)

                if face_distances[best_match_index] < 0.5:  # Only consider close matches
                    name = known_ids[best_match_index]

            # Scale back face locations to original frame size
            top, right, bottom, left = [val * 2 for val in location]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    except Exception as e:
        print(f"Face Recognition Error: {str(e)}")

    return frame, name
