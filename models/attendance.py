from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

#  Model for Raw Attendance Records (Daily)
class AttendanceRecord(BaseModel):
    emp_id: str
    date: datetime
    status: str  # Present, Absent, Late, etc.

#  Model for Weekly Attendance Summary
class WeeklyAttendance(BaseModel):
    emp_id: str
    week_start: datetime
    week_end: datetime
    total_present: int
    total_absent: int
    total_late: int

#  Model for Monthly Attendance Summary
class MonthlyAttendance(BaseModel):
    emp_id: str
    month: int  # 1 to 12
    year: int
    total_present: int
    total_absent: int
    total_late: int

#  Model for Yearly Attendance Summary
class YearlyAttendance(BaseModel):
    emp_id: str
    year: int
    total_present: int
    total_absent: int
    total_late: int
