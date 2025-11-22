from fastapi import APIRouter, HTTPException, Depends
from app.services.timeslot_service import TimeslotService
from app.core.deps import get_timeslot_service
from app.schemas.timeslot import TimeslotResponse, TimeslotListResponse

router = APIRouter()


@router.get("/", response_model=TimeslotListResponse)
async def get_all_timeslots(
    timeslot_service: TimeslotService = Depends(get_timeslot_service)
) -> TimeslotListResponse:
    return await timeslot_service.get_all_timeslots()


@router.get("/{timeslot_id}", response_model=TimeslotResponse)
async def get_timeslot_by_id(
    timeslot_id: int,
    timeslot_service: TimeslotService = Depends(get_timeslot_service)
) -> TimeslotResponse:
    timeslot = await timeslot_service.get_timeslot_by_id(timeslot_id)
    if not timeslot:
        raise HTTPException(status_code=404, detail="Timeslot not found")
    return timeslot

