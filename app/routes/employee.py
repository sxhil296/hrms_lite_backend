from fastapi import APIRouter, HTTPException, status, Query
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with same ID or email already exists"
        )

    result = await employee_collection.insert_one(employee.dict())

    return {
        "message": "Employee created successfully",
        "id": str(result.inserted_id)
    }

@router.get("/")
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    search: str = Query("", min_length=0)
):
    skip = (page - 1) * limit

    query = {}

    if search:
        query = {
            "$or": [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"employee_id": {"$regex": search, "$options": "i"}},
            ]
        }

    total = await employee_collection.count_documents(query)

    cursor = (
        employee_collection
        .find(query)
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )

    employees = []

    async for emp in cursor:
        emp["id"] = str(emp["_id"])
        del emp["_id"]
        employees.append(emp)

    return {
        "data": employees,
        "total": total,
        "page": page,
        "limit": limit,
        "hasNext": (total > page * limit),
        "totalPages": (total + limit - 1) // limit
    }


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