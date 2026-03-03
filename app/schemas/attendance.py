from pydantic import BaseModel
from datetime import date

class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: str