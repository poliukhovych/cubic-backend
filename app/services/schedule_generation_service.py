import httpx
import os
import asyncio
import json
import logging
from typing import List, Dict, Any

# Services for 'catalog' data
from .group_service import GroupService
from .teacher_preference_service import TeacherPreferenceService
from .teacher_service import TeacherService
from .room_service import RoomService
from .course_service import CourseService
from .timeslot_service import TimeslotService

# Services for 'links' and 'constraints'
from .group_course_service import GroupCourseService
from .teacher_course_service import TeacherCourseService
from .subgroup_constraint_service import SubgroupConstraintService

# Services for 'availability' and 'preferences'
from .teacher_availability_service import TeacherAvailabilityService
from .group_unavailability_service import GroupUnavailabilityService

# Services for 'saving' the result
from .schedule_service import ScheduleService
from .assignment_service import AssignmentService

# Import response schemas
from app.schemas.assignment import AssignmentResponse

SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://localhost:8000")

logger = logging.getLogger(__name__)


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
            teacher_preference_service: TeacherPreferenceService,
            group_unavailability_service: GroupUnavailabilityService,
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
        self.teacher_preference_service = teacher_preference_service
        self.group_unavailability_service = group_unavailability_service
        # Saving
        self.schedule_service = schedule_service
        self.assignment_service = assignment_service

        self.scheduler_url = SCHEDULER_URL

    async def _format_data_for_scheduler(self) -> Dict[str, Any]:
        """
        Fetches data from all services and transforms it into the complex
        'instance' JSON required by the scheduling microservice.
        """
        logger.info("=== Початок збору даних з БД ===")

        logger.info("Отримуємо викладачів з БД...")
        teachers_resp = await self.teacher_service.get_all_teachers()
        logger.info(f"Отримано з БД викладачів: {len(teachers_resp.teachers)}")
        if teachers_resp.teachers:
            logger.info(f"Список викладачів з БД: {[f'{t.last_name} {t.first_name} (id={t.teacher_id})' for t in teachers_resp.teachers]}")
        else:
            logger.warning("З БД не отримано жодного викладача!")

        logger.info("Отримуємо часові слоти з БД...")
        try:
            timeslots_all = await self.timeslot_service.get_all_formatted()
            if not timeslots_all:
                logger.warning("  З БД не отримано жодного часового слота! Використовуються fallback слотів.")
                timeslots_all = [
                    "mon.all.1", "mon.all.2", "mon.all.3", "mon.all.4",
                    "tue.all.1", "tue.all.2", "tue.all.3", "tue.all.4",
                    "wed.all.1", "wed.all.2", "wed.all.3", "wed.all.4",
                    "thu.all.1", "thu.all.2", "thu.all.3", "thu.all.4",
                    "fri.all.1", "fri.all.2", "fri.all.3", "fri.all.4"
                ]
                logger.info(f"Використано fallback слотів: {len(timeslots_all)}")
            else:
                logger.info(f"Отримано з БД часових слотів: {len(timeslots_all)}")
        except Exception as e:
            logger.error(f" Помилка при отриманні часових слотів: {e}")
            logger.error("   Використовуються fallback placeholder слотів.")
            timeslots_all = [
                "mon.all.1", "mon.all.2", "mon.all.3", "mon.all.4",
                "tue.all.1", "tue.all.2", "tue.all.3", "tue.all.4",
                "wed.all.1", "wed.all.2", "wed.all.3", "wed.all.4",
                "thu.all.1", "thu.all.2", "thu.all.3", "thu.all.4",
                "fri.all.1", "fri.all.2", "fri.all.3", "fri.all.4"
            ]
            logger.info(f"Використано fallback слотів: {len(timeslots_all)}")
        
        teachers_payload = []
        for t in teachers_resp.teachers:
            available_slots = await self.teacher_availability_service.get_teacher_availability_ids(t.teacher_id)
  
            if not available_slots:
                available_slots = timeslots_all.copy()
                logger.warning(f"⚠️  Викладач {t.last_name} {t.first_name} не має налаштованої доступності - вважаємо доступним у всіх {len(available_slots)} слотах")
            
            prefs_dict = await self.teacher_preference_service.get_preferences(t.teacher_id)
            
            prefs_formatted = {}
            if prefs_dict:
                if "preferred_days" in prefs_dict and prefs_dict["preferred_days"]:
                    prefs_formatted["preferred_days"] = prefs_dict["preferred_days"]
                if "avoid_slots" in prefs_dict and prefs_dict["avoid_slots"]:
                    prefs_formatted["avoid_slots"] = prefs_dict["avoid_slots"]
            
            teacher_entry = {
                "id": str(t.teacher_id),
                "name": f"{t.last_name} {t.first_name}",
                "available": available_slots,
                "prefs": prefs_formatted if prefs_formatted else {}
            }
            teachers_payload.append(teacher_entry)
            
            logger.info(f"Викладач {t.last_name} {t.first_name}: {len(available_slots)} доступних слотів")

        logger.info("Отримуємо групи з БД...")
        groups_models = await self.group_service.get_all_groups_as_models()
        logger.info(f"Отримано з БД груп: {len(groups_models)}")
        if groups_models:
            logger.info(f"Список груп з БД: {[f'{g.name} (id={g.group_id}, size={g.size}, parent={g.parent_group_id})' for g in groups_models]}")
        else:
            logger.warning("З БД не отримано жодної групи!")

        groups_payload = []
        for g in groups_models:
            unavailable_slots = await self.group_unavailability_service.get_group_unavailability_ids(g.group_id)
            
            group_entry = {
                "id": str(g.group_id),
                "name": g.name,
                "size": g.size,
                "unavailable": unavailable_slots if unavailable_slots else []
            }
            
            if g.parent_group_id:
                group_entry["parentGroupId"] = str(g.parent_group_id)
                logger.debug(f"Група {g.name} є підгрупою батьківської групи {g.parent_group_id}")
            
            groups_payload.append(group_entry)
            
            if unavailable_slots:
                logger.debug(f"Група {g.name}: {len(unavailable_slots)} недоступних слотів")

        logger.info("Отримуємо аудиторії з БД...")
        rooms_resp = await self.room_service.get_all_rooms()
        logger.info(f"Отримано з БД аудиторій: {len(rooms_resp.rooms)}")
        if rooms_resp.rooms:
            logger.info(f"Список аудиторій з БД: {[f'{r.name} (id={r.room_id}, capacity={r.capacity})' for r in rooms_resp.rooms]}")
        else:
            logger.warning("з БД не отримано жодної аудиторії!")

        rooms_payload = [
            {"id": str(r.room_id), "name": r.name, "capacity": r.capacity}
            for r in rooms_resp.rooms
        ]

        logger.info("Отримуємо курси з БД...")
        
        courses_resp = await self.course_service.get_all_courses()
        logger.info(f"Отримано курсів з CourseService: {len(courses_resp.courses)}")
        
        group_courses = await self.group_course_service.get_all_links()
        logger.info(f"Отримано зв'язків групи-курси: {len(group_courses)}")
        if group_courses:
            logger.info(f"Приклади GroupCourse зв'язків: {[(gc.course_id, gc.group_id, gc.count_per_week) for gc in group_courses[:3]]}")
        
        teacher_courses = await self.teacher_course_service.get_all_links()
        logger.info(f"Отримано зв'язків викладачі-курси: {len(teacher_courses)}")
        if teacher_courses:
            logger.info(f"Приклади TeacherCourse зв'язків: {[(tc.course_id, tc.teacher_id) for tc in teacher_courses[:3]]}")
        
        courses_dict = {course.course_id: course for course in courses_resp.courses}
        
        teachers_by_course = {}
        for tc in teacher_courses:
            if tc.course_id not in teachers_by_course:
                teachers_by_course[tc.course_id] = []
            teachers_by_course[tc.course_id].append(tc.teacher_id)
        
        logger.info(f"Створено словник викладачів по курсах: {len(teachers_by_course)} курсів мають призначених викладачів")
        
        courses_map = {}  
        skipped_courses = []
        
        for gc in group_courses:
            course = courses_dict.get(gc.course_id)
            if not course:
                skipped_courses.append(f"Курс ID={gc.course_id} не знайдено")
                logger.warning(f"Курс з ID {gc.course_id} не знайдено в списку курсів, пропускаємо зв'язок GroupCourse")
                continue
            
            teachers_for_course = teachers_by_course.get(gc.course_id, [])
            if not teachers_for_course:
                skipped_courses.append(f"Курс '{course.name}' (ID={gc.course_id}) без викладача")
                logger.warning(f" Для курсу '{course.name}' (ID: {gc.course_id}) не знайдено викладача, пропускаємо")
                continue
            
            teacher_id = teachers_for_course[0]
            

            try:
                frequency_value = gc.frequency.value.lower() if hasattr(gc.frequency, 'value') else str(gc.frequency).lower()
            except Exception as e:
                logger.warning(f" Помилка при обробці frequency для курсу {course.name}: {e}, використовуємо 'weekly'")
                frequency_value = "weekly"
            
            
            course_key = (gc.course_id, teacher_id, gc.count_per_week, frequency_value)
            
            if course_key not in courses_map:
                courses_map[course_key] = {
                    "course": course,
                    "teacher_id": teacher_id,
                    "count_per_week": gc.count_per_week,
                    "frequency": frequency_value,
                    "group_ids": []
                }
            
            courses_map[course_key]["group_ids"].append(str(gc.group_id))
            logger.debug(f"Додано групу {gc.group_id} до курсу {course.name} (teacher={teacher_id}, count={gc.count_per_week}, freq={frequency_value})")
    
        courses_payload = []
        for course_key, course_data in courses_map.items():
            course_id, teacher_id, count_per_week, frequency = course_key
            course = course_data["course"]
            
 
            unique_course_id = f"{course_id}_{count_per_week}_{frequency}"
            
            course_entry = {
                "id": unique_course_id,
                "name": course.name,
                "groupIds": course_data["group_ids"],
                "teacherId": str(teacher_id),
                "countPerWeek": count_per_week,
                "frequency": frequency
            }
            
            courses_payload.append(course_entry)
            logger.info(f" Створено курс: {course.name} (id={unique_course_id}, groups={len(course_data['group_ids'])}, teacher={teacher_id}, count={count_per_week}, freq={frequency})")
        
        logger.info(f"Сформовано courses_payload: {len(courses_payload)} курсів")
        
        if skipped_courses:
            logger.warning(f"Пропущено {len(skipped_courses)} курсів через відсутність даних:")
            for skip_reason in skipped_courses[:5]:  
                logger.warning(f"   - {skip_reason}")
        
        if courses_payload:
            logger.info(f"Приклади сформованих курсів: {[{'name': c['name'], 'count': c['countPerWeek'], 'freq': c['frequency']} for c in courses_payload[:3]]}")
        else:
            logger.error("КРИТИЧНА ПОМИЛКА: courses_payload порожній після обробки!")
            logger.error(f"   Кількість курсів в БД: {len(courses_resp.courses)}")
            logger.error(f"   Кількість GroupCourse зв'язків: {len(group_courses)}")
            logger.error(f"   Кількість TeacherCourse зв'язків: {len(teacher_courses)}")


        logger.info("Використовуємо часові слоти (вже отримані раніше)...")
        timeslots_payload = timeslots_all
        logger.info(f"Використовується {len(timeslots_payload)} часових слотів")
        if timeslots_payload:
            logger.info(f"Приклади часових слотів: {timeslots_payload[:5]}")
            all_count = len([ts for ts in timeslots_payload if '.all.' in ts])
            odd_count = len([ts for ts in timeslots_payload if '.odd.' in ts])
            even_count = len([ts for ts in timeslots_payload if '.even.' in ts])
            logger.info(f"Розподіл слотів: ALL={all_count}, ODD={odd_count}, EVEN={even_count}")
        else:
            logger.warning(" Немає часових слотів Використовуються мінімальні placeholder слотів.")
            timeslots_payload = [
                "mon.all.1", "mon.all.2", "mon.all.3", "mon.all.4",
                "tue.all.1", "tue.all.2", "tue.all.3", "tue.all.4",
                "wed.all.1", "wed.all.2", "wed.all.3", "wed.all.4",
                "thu.all.1", "thu.all.2", "thu.all.3", "thu.all.4",
                "fri.all.1", "fri.all.2", "fri.all.3", "fri.all.4"
            ]
            logger.info(f"Використано fallback слотів: {len(timeslots_payload)}")
            if not timeslots_all:
                timeslots_all = timeslots_payload
        
        if timeslots_payload:
            total_courses_slots = sum(c.get('countPerWeek', 1) for c in courses_payload)
            all_slots = len([ts for ts in timeslots_payload if '.all.' in ts])
            if all_slots < total_courses_slots:
                logger.warning(f"Може бути недостатньо слотів для генерування розкладу!")
                logger.warning(f"   Потрібно приблизно {total_courses_slots} слотів (для курсів з countPerWeek),")
                logger.warning(f"   але доступно тільки {all_slots} слотів з частотою 'all'.")
                logger.warning(f"   Всього слотів: {len(timeslots_payload)}")
        else:
            logger.error("КРИТИЧНА ПОМИЛКА: Немає часових слотів для генерування розкладу!")

        # --- Assemble Instance ---
        instance_data = {
            "teachers": teachers_payload,
            "groups": groups_payload,
            "rooms": rooms_payload,
            "courses": courses_payload,
            "timeslots": timeslots_payload,
        }

        logger.info("=== Завершено збір даних з БД ===")
        logger.info(f"Підсумок даних: викладачів={len(teachers_payload)}, груп={len(groups_payload)}, "
                   f"аудиторій={len(rooms_payload)}, курсів={len(courses_payload)}, часових слотів={len(timeslots_payload)}")
        
        # Валідація критичних даних
        validation_errors = []
        if not courses_payload:
            validation_errors.append("Немає курсів (courses_payload порожній)")
        if not teachers_payload:
            validation_errors.append("Немає викладачів")
        if not groups_payload:
            validation_errors.append("Немає груп")
        if not rooms_payload:
            validation_errors.append("Немає аудиторій")
        if not timeslots_payload:
            validation_errors.append("Немає часових слотів")
            
        if validation_errors:
            logger.error("КРИТИЧНІ ПОМИЛКИ ВАЛІДАЦІЇ:")
            for error in validation_errors:
                logger.error(f"   - {error}")

        return instance_data

    async def _convert_assignments_from_microservice(
            self, assignments_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Converts assignment data from microservice format to DB format.
        
        Microservice format:
        {
            "courseId": "uuid_2_weekly",  # includes countPerWeek and frequency
            "teacherId": "uuid",
            "roomId": "uuid",
            "timeslot": "mon.all.1",  # string format
            "groupIds": ["uuid1", "uuid2"]  # array
        }
        
        DB format (AssignmentCreate):
        {
            "courseId": "uuid",  # original UUID without suffix
            "teacherId": "uuid",
            "roomId": "uuid",
            "timeslotId": 123,  # integer
            "groupId": "uuid",  # single UUID
            "subgroupNo": 1,
            "courseType": "LEC"
        }
        """
        from uuid import UUID as UUIDType
        from app.db.models.common_enums import CourseType
        
        timeslot_map = await self.timeslot_service.get_string_to_id_map()
        
        converted = []
        
        for assignment in assignments_data:
            course_id_str = assignment.get("courseId", "")
            if "_" in course_id_str:
                original_course_id = course_id_str.split("_")[0]
            else:
                original_course_id = course_id_str
            
            try:
                course_id_uuid = UUIDType(original_course_id)
            except ValueError:
                logger.error(f"Невірний формат courseId: {course_id_str}")
                continue
            
            timeslot_str = assignment.get("timeslot", "")
            timeslot_id = timeslot_map.get(timeslot_str)
            if not timeslot_id:
                logger.error(f"Не знайдено timeslot_id для '{timeslot_str}'")
                continue
            
            teacher_id_str = assignment.get("teacherId", "")
            room_id_str = assignment.get("roomId")
            group_ids = assignment.get("groupIds", [])
            
            try:
                teacher_id_uuid = UUIDType(teacher_id_str)
            except ValueError:
                logger.error(f" Невірний формат teacherId: {teacher_id_str}")
                continue
            
            room_id_uuid = None
            if room_id_str:
                try:
                    room_id_uuid = UUIDType(room_id_str)
                except ValueError:
                    logger.warning(f"Невірний формат roomId: {room_id_str}, встановлюємо None")
                    room_id_uuid = None
            

            COURSE_TYPE_MAP = {
                "LEC": "lec",
                "PRAC": "prac",
                "LAB": "lab"
            }
            course_type_python = CourseType.LEC  
            course_type_db = COURSE_TYPE_MAP.get(course_type_python.value, "lec")  
            
            for group_id_str in group_ids:
                try:
                    group_id_uuid = UUIDType(group_id_str)
                except ValueError:
                    logger.error(f" Невірний формат groupId: {group_id_str}")
                    continue
                
                converted_assignment = {
                    "courseId": str(course_id_uuid),
                    "teacherId": str(teacher_id_uuid),
                    "roomId": str(room_id_uuid) if room_id_uuid else None,
                    "timeslotId": timeslot_id,
                    "groupId": str(group_id_uuid),
                    "subgroupNo": 1,  
                    "courseType": course_type_db  
                }
                
                converted.append(converted_assignment)
                logger.debug(f"Конвертовано призначення: course={course_id_uuid}, group={group_id_uuid}, timeslot={timeslot_id}")
        
        return converted

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
        logger.info("=" * 80)
        logger.info("=== ПОЧАТОК ГЕНЕРАЦІЇ РОЗКЛАДУ ===")
        logger.info("=" * 80)
        logger.info(f" Параметри запиту:")
        logger.info(f"   - schedule_label: '{schedule_label}'")
        logger.info(f"   - policy: {json.dumps(policy, ensure_ascii=False)}")
        logger.info(f"   - params: {json.dumps(params, ensure_ascii=False)}")
        
        logger.info("\n Формування даних для мікросервісу...")
        instance_data = await self._format_data_for_scheduler()

        payload = {
            "instance": {
                **instance_data,
                "policy": policy
            },
            "params": params
        }

        logger.info("\n" + "=" * 80)
        logger.info("=== ВІДПРАВКА ДАНИХ НА МІКРОСЕРВІС ===")
        logger.info("=" * 80)
        logger.info(f" URL мікросервісу: {self.scheduler_url}/v1/solve")
        
        courses_count = len(instance_data.get('courses', []))
        teachers_count = len(instance_data.get('teachers', []))
        groups_count = len(instance_data.get('groups', []))
        rooms_count = len(instance_data.get('rooms', []))
        timeslots_count = len(instance_data.get('timeslots', []))
        
        logger.info(f"\n Структура payload:")
        logger.info(f"   - Викладачів: {teachers_count}")
        logger.info(f"   - Груп: {groups_count}")
        logger.info(f"   - Аудиторій: {rooms_count}")
        logger.info(f"   - Курсів: {courses_count}")
        logger.info(f"   - Часових слотів: {timeslots_count}")
        logger.info(f"   - Policy: {bool(policy)}")
        logger.info(f"   - Params: {bool(params)}")
        
        warnings = []
        if courses_count == 0:
            warnings.append("КРИТИЧНО: 0 курсів - мікросервіс не зможе створити розклад!")
        if teachers_count == 0:
            warnings.append("0 викладачів")
        if groups_count == 0:
            warnings.append("0 груп")
        if rooms_count == 0:
            warnings.append("0 аудиторій")
        if timeslots_count < 5:
            warnings.append(f" Мало часових слотів ({timeslots_count}) - може бути недостатньо для створення розкладу")
            
        if warnings:
            logger.warning("\n  ПОПЕРЕДЖЕННЯ:")
            for warning in warnings:
                logger.warning(f"   {warning}")
        
        logger.info(f"\n Повний JSON payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")

        async with httpx.AsyncClient() as client:
            
            try:
                logger.info("\n Відправка запиту на мікросервіс...")
                response = await client.post(
                    f"{self.scheduler_url}/v1/solve", json=payload, timeout=20.0
                )
                response.raise_for_status()
                job_id = response.json()["jobId"]
                logger.info(f"Завдання створено успішно! Job ID: {job_id}")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(f" Помилка при створенні завдання: {e}")
                logger.error(f"   URL: {self.scheduler_url}/v1/solve")
                if hasattr(e, 'response') and e.response:
                    logger.error(f"   Response status: {e.response.status_code}")
                    logger.error(f"   Response body: {e.response.text}")
                raise Exception(f"Failed to start scheduling job: {e}")

            logger.info(f"\n⏳ Очікування виконання завдання {job_id}...")
            poll_count = 0
            while True:
                await asyncio.sleep(3)
                poll_count += 1
                logger.debug(f"   Спроба #{poll_count}: перевірка статусу завдання...")
                
                try:
                    result_response = await client.get(
                        f"{self.scheduler_url}/v1/jobs/{job_id}/result", timeout=10.0
                    )

                    if result_response.status_code == 200:
                        logger.info(f"\nЗавдання виконано після {poll_count} спроб!")
                        result_json = result_response.json()
                        assignments_data = result_json.get("assignments", [])
                        
                        logger.info("\n" + "=" * 80)
                        logger.info("=== ОТРИМАНО ВІДПОВІДЬ З МІКРОСЕРВІСУ ===")
                        logger.info("=" * 80)
                        logger.info(f"Повна відповідь:\n{json.dumps(result_json, ensure_ascii=False, indent=2, default=str)}")
                        
                        status = result_json.get("status", "unknown")
                        stats_status = result_json.get("stats", {}).get("status", "unknown")
                        solve_time = result_json.get("stats", {}).get("solve_time_sec", 0)
                        objective = result_json.get("objective", 0)
                        violations = result_json.get("violations", [])
                        
                        logger.info(f"\nСтатистика виконання:")
                        logger.info(f"   - Статус: {status}")
                        logger.info(f"   - Solver статус: {stats_status}")
                        logger.info(f"   - Час виконання: {solve_time:.4f} сек")
                        logger.info(f"   - Objective: {objective}")
                        logger.info(f"   - Кількість призначень: {len(assignments_data)}")
                        logger.info(f"   - Порушення: {len(violations)}")
                        
                        if violations:
                            logger.warning(f"\n  Виявлено порушення:")
                            for v in violations:
                                logger.warning(f"   - {v}")
                        
                        if status == "infeasible":
                            logger.error("\n МІКРОСЕРВІС НЕ ЗМІГ ЗНАЙТИ РІШЕННЯ (INFEASIBLE)")
                            logger.error("   Можливі причини:")
                            logger.error("   1. Занадто жорсткі обмеження (недостатньо часових слотів)")
                            logger.error("   2. Конфлікт у доступності викладачів/груп/аудиторій")
                            logger.error("   3. Недостатньо аудиторій для кількості груп")
                            logger.error("   4. Викладач призначений на надто багато курсів")
                            logger.error(f"\n   Спробуйте:")
                            logger.error(f"   - Збільшити кількість часових слотів (зараз: {timeslots_count})")
                            logger.error(f"   - Перевірити конфлікти в доступності")
                            logger.error(f"   - Зменшити count_per_week для деяких курсів")
                        elif not assignments_data:
                            logger.error("\n МІКРОСЕРВІС ПОВЕРНУВ 0 ПРИЗНАЧЕНЬ")
                            logger.error(f"   Статус: {status}, Solver: {stats_status}")
                            if status == "solved" or stats_status == "OPTIMAL":
                                logger.error("   Це дивно - статус 'solved', але немає призначень!")
                                logger.error("   Перевірте вхідні дані (особливо courses_payload)")
                        else:
                            logger.info(f"\nУспішно створено {len(assignments_data)} призначень!")
                            logger.info(f"   Приклад першого призначення:")
                            logger.info(f"   {json.dumps(assignments_data[0], ensure_ascii=False, indent=4, default=str)}")

                        logger.info("\n" + "=" * 80)
                        logger.info("=== ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТУ В БД ===")
                        logger.info("=" * 80)
                        new_schedule = await self.schedule_service.create_schedule(
                            label=schedule_label
                        )
                        logger.info(f" Створено розклад: ID={new_schedule.schedule_id}, label='{new_schedule.label}'")

                        if assignments_data:
                            logger.info(f"\nКонвертація та збереження {len(assignments_data)} призначень...")
                            
                            converted_assignments = await self._convert_assignments_from_microservice(assignments_data)
                            logger.info(f" Конвертовано {len(converted_assignments)} призначень для збереження")
                            
                            saved_assignments = await self.assignment_service.create_assignments(
                                schedule_id=new_schedule.schedule_id,
                                assignments_data=converted_assignments
                            )
                            logger.info(f"Збережено {len(saved_assignments)} призначень в БД")
                        else:
                            logger.warning("  Немає призначень для збереження")
                            saved_assignments = []
                        
                        logger.info("\n" + "=" * 80)
                        logger.info("=== ГЕНЕРАЦІЯ РОЗКЛАДУ ЗАВЕРШЕНА ===")
                        logger.info("=" * 80)
                        logger.info(f" Підсумок:")
                        logger.info(f"   - Schedule ID: {new_schedule.schedule_id}")
                        logger.info(f"   - Збережено призначень: {len(saved_assignments)}")
                        logger.info(f"   - Статус: {status}")
                        logger.info("=" * 80 + "\n")
                        
                        return saved_assignments

                    elif result_response.status_code == 500:
                        error_details = result_response.json().get("detail", "Unknown error")
                        logger.error(f"\n Завдання {job_id} завершилось з помилкою:")
                        logger.error(f"   {error_details}")
                        raise Exception(f"Scheduling job {job_id} failed: {error_details}")

                except httpx.RequestError as e:
                    logger.warning(f" Помилка при перевірці статусу (спроба #{poll_count}): {e}")
                    logger.warning("   Повторна спроба через 3 секунди...")
                    continue