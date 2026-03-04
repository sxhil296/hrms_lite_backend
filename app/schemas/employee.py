from pydantic import BaseModel, EmailStr

class EmployeeCreate(BaseModel):
    full_name: str
    email: EmailStr
    department: str