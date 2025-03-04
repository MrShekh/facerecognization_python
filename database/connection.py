from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"  # Update if using a remote DB
DB_NAME = "ai_attendance_system"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


# ✅ Collections (Tables)
attendance_collection = db["attendance_records"]
weekly_attendance_collection = db["weekly_attendance"]
monthly_attendance_collection = db["monthly_attendance"]
yearly_attendance_collection = db["yearly_attendance"]