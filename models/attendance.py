from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Attendance Schema for validation
class Attendance(BaseModel):
    student_id: str  # Unique ID of the student
    name: str  # Student's full name
    subject: str  # Subject name
    date: str  # Date of attendance (YYYY-MM-DD format)
    timestamp: Optional[datetime] = datetime.utcnow()  # Automatic timestamp
    status: str  # "Present" or "Absent"

    class Config:
        orm_mode = True  # Allows ORM compatibility (if needed in the future)
