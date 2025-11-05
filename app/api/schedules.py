from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# from ..database import get_db
# from .. import schemas, crud
from app.services import scheduler_client


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)


@router.post("/generate")
async def generate_new_schedule(db: Session = Depends(get_db)):
    try:
        # Calling microservice
        assignments_data = await scheduler_client.generate_schedule_and_wait(db)

        # Adapt and save result to DB
        # Start of block to be adapted
        # Here we should call our CRUD function for saving
        # validated_assignments = [schemas.Assignment.model_validate(a) for a in assignments_data]
        # saved_assignments = crud.save_schedule(db, validated_assignments)
        # End of block to be adapted

        # Returning result to frontend
        return {
            "message": f"Successfully generated a new schedule with {len(assignments_data)} assignments.",
            "schedule": assignments_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
