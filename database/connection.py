from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"  # Update if using a remote DB
DB_NAME = "ai_attendance_system"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
