import httpx
import asyncio
import os
from sqlalchemy.orm import Session
# we need to import real CRUD functions and models
# from . import crud, models
from typing import List, Dict, Any

SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://localhost:8000")

def format_data_for_scheduler(db: Session) -> Dict[str, Any]:
    """
    Collects data from database and formats it into JSON,
    which the scheduling microservice expects.
    """
    # Start of block to be adapted
    # Here we call our CRUD functions to get data
    # For example:
    # teachers = crud.get_teachers(db)
    # groups = crud.get_groups(db)
    # rooms = crud.get_rooms(db)
    # courses = crud.get_courses(db)

    # Temporary zaglushki
    teachers = [{'id': 't_kovalenko', 'name': 'Коваленко О.'}]
    groups = [{'id': 'g_cs_1', 'name': 'Комп. науки-1', 'size': 30}]
    rooms = [{'id': 'r101', 'name': 'Ауд. 101', 'capacity': 35}]
    courses = [{'id': 'c_prog', 'name': 'Програмування', 'countPerWeek': 2, 'teacher_id': 't_kovalenko',
                'groups': [{'id': 'g_cs_1'}]}]
    # End of block to be adapted

    static_data = {
        "timeslots": ["mon.all.1", "mon.all.2", "mon.all.3", "tue.all.1", "tue.all.2"],
        "policy": {"soft_weights": {"windows_penalty": 20}},
        "params": {"timeLimitSec": 15}
    }

    teachers_payload = [
        {"id": t['id'], "name": t['name'], "available": static_data["timeslots"], "prefs": {}}
        for t in teachers
    ]
    groups_payload = [{"id": g['id'], "name": g['name'], "size": g['size']} for g in groups]
    rooms_payload = [{"id": r['id'], "name": r['name'], "capacity": r['capacity']} for r in rooms]
    courses_payload = [
        {"id": c['id'], "name": c['name'], "groupIds": [g['id'] for g in c['groups']], "teacherId": c['teacher_id'],
         "countPerWeek": c['countPerWeek']}
        for c in courses
    ]

    payload = {
        "instance": {
            "teachers": teachers_payload, "groups": groups_payload,
            "rooms": rooms_payload, "courses": courses_payload,
            "timeslots": static_data["timeslots"], "policy": static_data["policy"]
        },
        "params": static_data["params"]
    }
    return payload


async def generate_schedule_and_wait(db: Session) -> List[Dict[str, Any]]:
    payload = format_data_for_scheduler(db)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{SCHEDULER_URL}/v1/solve", json=payload, timeout=10)
            response.raise_for_status()
            job_id = response.json()["jobId"]
            print(f"Scheduling job started with ID: {job_id}")
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            raise Exception(f"Failed to start scheduling job: {e}")

        while True:
            await asyncio.sleep(3)
            print(f"Polling for result of job ID: {job_id}...")
            try:
                result_response = await client.get(f"{SCHEDULER_URL}/v1/jobs/{job_id}/result", timeout=10)

                if result_response.status_code == 200:
                    print("Job successfully solved!")
                    return result_response.json()["assignments"]
                elif result_response.status_code == 500:
                    error_details = result_response.json().get("detail", "Unknown error")
                    raise Exception(f"Scheduling job failed: {error_details}")

            except httpx.RequestError as e:
                print(f"Polling failed, retrying... Error: {e}")
