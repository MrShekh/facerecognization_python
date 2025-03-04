# Face Recognition Attendance System

## Overview
This project is a **Face Recognition-based Attendance System** built with **FastAPI**, **OpenCV**, and **Face Recognition**. It allows users to register with their images and automatically marks attendance when their face is detected.

## Features
- **User Registration**: Add new users with a profile picture.
- **Face Recognition**: Identifies users from a live camera feed.
- **Attendance Marking**: Marks attendance when a face is recognized.
- **Duplicate Prevention**: Prevents multiple attendance entries within a defined time frame.
- **MongoDB Integration**: Stores user data and attendance records.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Face Recognition**: dlib, face_recognition, OpenCV
- **Database**: MongoDB
- **Cloud Storage**: Local storage (can be extended to AWS S3, Firebase, etc.)

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- MongoDB (Running instance)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```

## API Endpoints
### 1. Add User
**Endpoint:** `POST /add-user`
- **Params:** `emp_id`, `name`, `role`, `department`, `photo`
- **Description:** Uploads an image and stores user data.

### 2. Mark Attendance
**Endpoint:** `POST /api/mark-attendance`
- **Params:** Image file
- **Description:** Recognizes face and marks attendance if detected.

## Usage
1. Add users to the system via `/add-user`.
2. Capture images for attendance via `/api/mark-attendance`.
3. Attendance is stored in the MongoDB database.

## Future Enhancements
- Implement real-time video stream processing.
- Add support for cloud-based storage (AWS, Firebase).
- Improve face recognition accuracy using deep learning.

## Contributing
Feel free to submit pull requests or open issues to suggest improvements!

## License
This project is licensed under the MIT License.

---
### Author
**Your Name**  
GitHub: [yourusername](https://github.com/yourusername)

