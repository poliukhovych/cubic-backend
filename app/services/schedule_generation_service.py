import httpx
import os
import asyncio
from typing import List, Dict, Any

# --- Import ALL required services for orchestration ---

# Services for 'catalog' data
from .group_service import GroupService
from .teacher_service import TeacherService
from .room_service import RoomService
from .course_service import CourseService
from .timeslot_service import TimeslotService  # TODO: Must be created

# Services for 'links' and 'constraints'
from .group_course_service import GroupCourseService  # TODO: Must be created
from .teacher_course_service import TeacherCourseService  # TODO: Must be created
from .subgroup_constraint_service import SubgroupConstraintService  # TODO: Must be created

# Services for 'availability' and 'preferences'
from .teacher_availability_service import TeacherAvailabilityService  # TODO: Must be created
from .group_availability_service import GroupAvailabilityService  # TODO: Must be created

# Services for 'saving' the result
from .schedule_service import ScheduleService  # This is the renamed ScheduleLogService
from .assignment_service import AssignmentService

# Import response schemas
from app.schemas.assignment import AssignmentResponse

SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://localhost:8000")


class ScheduleGenerationService:
    """
    Orchestrates the schedule generation process.
    - Fetches data from ~10 different services.
    - Assembles the complex JSON 'problem instance'.
    - Calls the external microservice and polls for results.
    - Saves the resulting assignments back to the DB.
    """

    def __init__(
            self,
            # Catalog services
            group_service: GroupService,
            teacher_service: TeacherService,
            room_service: RoomService,
            course_service: CourseService,
            timeslot_service: TimeslotService,
            # Constraint services
            group_course_service: GroupCourseService,
            teacher_course_service: TeacherCourseService,
            subgroup_constraint_service: SubgroupConstraintService,
            # Availability services
            teacher_availability_service: TeacherAvailabilityService,
            group_availability_service: GroupAvailabilityService,
            # Saving services
            schedule_service: ScheduleService,
            assignment_service: AssignmentService
    ):
        # Catalog
        self.group_service = group_service
        self.teacher_service = teacher_service
        self.room_service = room_service
        self.course_service = course_service
        self.timeslot_service = timeslot_service
        # Constraints
        self.group_course_service = group_course_service
        self.teacher_course_service = teacher_course_service
        self.subgroup_constraint_service = subgroup_constraint_service
        # Availability
        self.teacher_availability_service = teacher_availability_service
        self.group_availability_service = group_availability_service
        # Saving
        self.schedule_service = schedule_service
        self.assignment_service = assignment_service

        self.scheduler_url = SCHEDULER_URL

    async def _format_data_for_scheduler(self) -> Dict[str, Any]:
        """
        Fetches data from all services and transforms it into the complex
        'instance' JSON required by the scheduling microservice.
        """

        # --- 1. Fetch Teachers Payload ---
        teachers_resp = await self.teacher_service.get_all_teachers()

        # TODO: GAP 1 - Fetch availability/preferences
        # We must implement TeacherAvailabilityService to get 'available'
        # and 'prefs' data for each teacher.
        # teachers_availability = await self.teacher_availability_service.get_all()
        teachers_payload = [
            {
                "id": t.teacher_id,
                "name": f"{t.last_name} {t.first_name}",
                "available": [],  # TODO: Get from teachers_availability
                "prefs": {}  # TODO: Get from teachers_availability
            }
            for t in teachers_resp.teachers
        ]

        # --- 2. Fetch Groups Payload ---
        groups_resp = await self.group_service.get_all_groups()

        # TODO: GAP 4 - Dynamically generate subgroups
        # We must fetch from SubgroupConstraintService and dynamically
        # create 'g_cs_1a', 'g_cs_1b' entries with 'parentGroupId'.
        # constraints = await self.subgroup_constraint_service.get_all()

        # TODO: GAP 1 - Fetch group unavailability
        # We must implement GroupAvailabilityService.
        # groups_unavailability = await self.group_availability_service.get_all()

        groups_payload = [
            {
                "id": g.group_id,
                "name": g.name,
                "size": g.size,
                "unavailable": []  # TODO: Get from groups_unavailability
            }
            for g in groups_resp.groups
        ]
        # TODO: Add the dynamically generated subgroups to groups_payload here.

        # --- 3. Fetch Rooms Payload ---
        rooms_resp = await self.room_service.get_all_rooms()
        rooms_payload = [
            {"id": r.room_id, "name": r.name, "capacity": r.capacity}
            for r in rooms_resp.rooms
        ]

        # --- 4. Fetch Courses (Classes) Payload ---

        # TODO: GAP 3 & 2 - Denormalize "classes"
        # This is the most complex part. We cannot just loop courses.
        # 1. Fetch from CourseService, GroupCourseService, TeacherCourseService.
        # 2. Loop through GroupCourse links. Each link is a "class".
        # 3. For each "class", find its teacher(s) from TeacherCourseService.
        # 4. For each "class", get 'countPerWeek' and 'frequency' (GAP 2).
        #    This data MUST be added to the 'group_course' table.
        # 5. Handle subgroup logic (GAP 4): if a class is for 'g_cs_1'
        #    and it has 2 subgroups, this *one* link might need to
        #    create *two* separate "class" objects in the JSON
        #    (e.g., "Programming (Lab A)" and "Programming (Lab B)").

        courses_payload = [
            # {
            #   "id": "c_prog_laba", # Dynamically generated ID
            #   "name": "Programming (Lab A)", # Dynamically generated name
            #   "groupIds": ["g_cs_1a"], # Must use the generated subgroup ID
            #   "teacherId": "t_petrenko", # From TeacherCourse link
            #   "countPerWeek": 1, # From GroupCourse link (NEEDS TO BE ADDED)
            #   "frequency": "even" # From GroupCourse link (NEEDS TO BE ADDED)
            # }
        ]

        # --- 5. Fetch Timeslots Payload ---

        # TODO: GAP 5 - Fetch timeslots with frequency
        # We must implement TimeslotService.
        # The 'timeslots' table MUST be updated to include an 'frequency'
        # column (all, odd, even) to support this.
        # We need to generate string IDs like "mon.all.1", "tue.even.1".

        # timeslots_resp = await self.timeslot_service.get_all_formatted()
        # timeslots_payload = timeslots_resp.timeslots

        timeslots_payload = ["mon.all.1", "mon.all.2"]  # Placeholder

        # --- Assemble Instance ---
        instance_data = {
            "teachers": teachers_payload,
            "groups": groups_payload,
            "rooms": rooms_payload,
            "courses": courses_payload,
            "timeslots": timeslots_payload,
        }

        return instance_data

    async def generate_and_save_schedule(
            self,
            policy: Dict[str, Any],
            params: Dict[str, Any],
            schedule_label: str
    ) -> List[AssignmentResponse]:
        """
        Full process: format data, call microservice, poll, save result.
        'policy' and 'params' are provided from the frontend request.
        """
        print("Formatting data for scheduler...")
        instance_data = await self._format_data_for_scheduler()

        # Combine DB data with frontend data to build final payload
        payload = {
            "instance": {
                **instance_data,
                "policy": policy  # Add policy from frontend
            },
            "params": params  # Add params from frontend
        }

        async with httpx.AsyncClient() as client:
            # 1. Start the job
            try:
                response = await client.post(
                    f"{self.scheduler_url}/v1/solve", json=payload, timeout=20.0
                )
                response.raise_for_status()
                job_id = response.json()["jobId"]
                print(f"Scheduling job started with ID: {job_id}")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                raise Exception(f"Failed to start scheduling job: {e}")

            # 2. Poll for the result
            while True:
                await asyncio.sleep(3)
                print(f"Polling for result of job ID: {job_id}...")
                try:
                    result_response = await client.get(
                        f"{self.scheduler_url}/v1/jobs/{job_id}/result", timeout=10.0
                    )

                    if result_response.status_code == 200:
                        # 3. Success - Got the result
                        print("Job successfully solved!")
                        assignments_data = result_response.json()["assignments"]

                        # 4. Create a parent schedule "folder" record
                        new_schedule = await self.schedule_service.create_schedule(
                            label=schedule_label
                        )
                        print(f"Created parent schedule: {new_schedule.schedule_id}")

                        # 5. Save the actual assignments
                        saved_assignments = await self.assignment_service.create_assignments(
                            schedule_id=new_schedule.schedule_id,
                            assignments_data=assignments_data
                        )
                        return saved_assignments

                    elif result_response.status_code == 500:
                        # Job failed on the solver side
                        error_details = result_response.json().get("detail", "Unknown error")
                        raise Exception(f"Scheduling job {job_id} failed: {error_details}")

                except httpx.RequestError as e:
                    print(f"Polling failed, retrying... Error: {e}")
