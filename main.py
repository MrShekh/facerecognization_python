from fastapi import FastAPI
from routes.attendance import router as attendance_router
from database.connection import db  # Ensure the database connection is imported

app = FastAPI()

app.include_router(attendance_router, prefix="/api")

@app.get("/")
async def home():
    return {"message": "AI Attendance System Backend is Running"}
