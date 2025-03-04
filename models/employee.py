from pydantic import BaseModel

class Employee(BaseModel):
    emp_id: str
    name: str
    role: str  # "employee", "student", "staff"
    photo: str  # File path of the stored image
    department: str = None  # Optional
