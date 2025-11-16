from typing import List, Dict

from app.repositories.timeslot_repository import TimeslotRepository


class TimeslotService:
    """
    Service for managing scheduling timeslots.
    Handles the conversion of DB records to string identifiers used by the solver.
    """

    _DAY_MAP = {
        1: "mon", 2: "tue", 3: "wed", 4: "thu", 5: "fri", 6: "sat", 7: "sun"
    }

    def __init__(self, repo: TimeslotRepository):
        self.repo = repo

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
            # enum value of frequency is used (e.g., 'all', 'odd', 'even')
            fmt_id = f"{day_str}.{ts.frequency.value}.{ts.lesson_id}"
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
            fmt_id = f"{day_str}.{ts.frequency.value}.{ts.lesson_id}"
            mapping[ts.timeslot_id] = fmt_id

        return mapping
