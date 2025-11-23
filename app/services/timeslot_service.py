from typing import List, Dict, Optional

from app.repositories.lesson_repository import LessonRepository

from app.repositories.timeslot_repository import TimeslotRepository
from app.schemas.timeslot import TimeslotResponse, LessonResponse, TimeslotListResponse


class TimeslotService:
    """
    Service for managing scheduling timeslots.
    Handles the conversion of DB records to string identifiers used by the solver.
    """

    _DAY_MAP = {
        1: "mon", 2: "tue", 3: "wed", 4: "thu", 5: "fri", 6: "sat", 7: "sun"
    }

    def __init__(self, repo: TimeslotRepository, lesson_repo: LessonRepository):
        self.repo = repo
        self.lesson_repo = lesson_repo

    async def get_all_formatted(self) -> List[str]:
        """
        Retrieves all timeslots and returns them as formatted strings
        expected by the microservice (e.g., 'mon.all.1', 'tue.even.2').
        """
        timeslots = await self.repo.find_all()
        formatted_ids = []

        for ts in timeslots:
            day_str = self._DAY_MAP.get(ts.day, "unknown")
            # format: "{day}.{frequency}.{lesson_id}"
            # enum value повертає "ALL", "ODD", "EVEN" - конвертуємо в нижній регістр
            frequency_str = ts.frequency.value.lower() if hasattr(ts.frequency, 'value') else str(ts.frequency).lower()
            fmt_id = f"{day_str}.{frequency_str}.{ts.lesson_id}"
            formatted_ids.append(fmt_id)

        return formatted_ids

    async def get_id_map(self) -> Dict[int, str]:
        """
        Returns a dictionary mapping DB Integer IDs to String IDs.
        Useful for resolving availability data.
        """
        timeslots = await self.repo.find_all()
        mapping = {}

        for ts in timeslots:
            day_str = self._DAY_MAP.get(ts.day, "unknown")
            # Конвертуємо frequency в нижній регістр для узгодженості з форматом мікросервісу
            frequency_str = ts.frequency.value.lower() if hasattr(ts.frequency, 'value') else str(ts.frequency).lower()
            fmt_id = f"{day_str}.{frequency_str}.{ts.lesson_id}"
            mapping[ts.timeslot_id] = fmt_id

        return mapping

    async def get_string_to_id_map(self) -> Dict[str, int]:
        """
        Returns a dictionary mapping String IDs (e.g., 'mon.all.1') to DB Integer IDs.
        Useful for converting microservice response back to DB format.
        """
        timeslots = await self.repo.find_all()
        mapping = {}

        for ts in timeslots:
            day_str = self._DAY_MAP.get(ts.day, "unknown")
            frequency_str = ts.frequency.value.lower() if hasattr(ts.frequency, 'value') else str(ts.frequency).lower()
            fmt_id = f"{day_str}.{frequency_str}.{ts.lesson_id}"
            mapping[fmt_id] = ts.timeslot_id

        return mapping

    async def get_all_timeslots(self) -> TimeslotListResponse:
        """
        Retrieves all timeslots with full information including lesson details.
        """
        timeslots = await self.repo.find_all()
        
        # Load all lessons
        all_lessons = await self.lesson_repo.find_all()
        lesson_map = {lesson.lesson_id: lesson for lesson in all_lessons}
        
        # Build timeslot responses
        timeslot_responses = []
        for ts in timeslots:
            lesson = lesson_map.get(ts.lesson_id)
            if not lesson:
                continue  # Skip if lesson not found
            
            lesson_response = LessonResponse.model_validate(lesson)
            timeslot_response = TimeslotResponse(
                timeslot_id=ts.timeslot_id,
                day=ts.day,
                frequency=ts.frequency,
                lesson=lesson_response
            )
            timeslot_responses.append(timeslot_response)
        
        return TimeslotListResponse(timeslots=timeslot_responses, total=len(timeslot_responses))

    async def get_timeslot_by_id(self, timeslot_id: int) -> Optional[TimeslotResponse]:
        """
        Retrieves a single timeslot by ID with full information including lesson details.
        """
        timeslot = await self.repo.find_by_id(timeslot_id)
        if not timeslot:
            return None
        
        lesson = await self.lesson_repo.find_by_id(timeslot.lesson_id)
        if not lesson:
            return None
        
        lesson_response = LessonResponse.model_validate(lesson)
        return TimeslotResponse(
            timeslot_id=timeslot.timeslot_id,
            day=timeslot.day,
            frequency=timeslot.frequency,
            lesson=lesson_response
        )
