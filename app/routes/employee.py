from fastapi import APIRouter, HTTPException, status
from app.database import employee_collection
from app.schemas.employee import EmployeeCreate

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):

   existing = await employee_collection.find_one({
    "$or": [
        {"employee_id": employee.employee_id},
        {"email": employee.email}
    ]
})

if existing:
    if existing["employee_id"] == employee.employee_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID already exists"
        )
    if existing["email"] == employee.email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    result = await employee_collection.insert_one(employee.dict())

    return {
        "message": "Employee created successfully",
        "id": str(result.inserted_id)
    }


@router.get("/")
async def get_employees():
    employees = []

    async for emp in employee_collection.find():
        emp["id"] = str(emp["_id"])
        del emp["_id"]
        employees.append(emp)

    return employees


@router.delete("/{employee_id}")
async def delete_employee(employee_id: str):

    result = await employee_collection.delete_one(
        {"employee_id": employee_id}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {"message": "Employee deleted successfully"}