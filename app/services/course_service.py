from typing import List, Optional, Dict, Any
import uuid


class CourseService:
    def __init__(self):
        self._courses = [
            {
                "id": "c1",
                "name": "Алгоритми та структури даних",
                "description": "Основи алгоритмів та структур даних",
                "credits": 6,
                "teacher_id": "t1"
            },
            {
                "id": "c2",
                "name": "Програмування на Python",
                "description": "Основи програмування на мові Python",
                "credits": 4,
                "teacher_id": "t1"
            },
            {
                "id": "c3",
                "name": "Математичний аналіз",
                "description": "Диференціальне та інтегральне числення",
                "credits": 8,
                "teacher_id": "t2"
            },
            {
                "id": "c4",
                "name": "Квантова механіка",
                "description": "Основи квантової механіки",
                "credits": 6,
                "teacher_id": "t3"
            },
            {
                "id": "c5",
                "name": "Веб-розробка",
                "description": "Створення веб-додатків",
                "credits": 5,
                "teacher_id": "t4"
            },
            {
                "id": "c6",
                "name": "Бази даних",
                "description": "Проектування та управління базами даних",
                "credits": 5,
                "teacher_id": "t4"
            },
            {
                "id": "c7",
                "name": "Машинне навчання",
                "description": "Основи машинного навчання та штучного інтелекту",
                "credits": 6,
                "teacher_id": "t1"
            }
        ]

    async def get_all_courses(self) -> List[Dict[str, Any]]:
        return self._courses

    async def get_courses_by_teacher_id(self, teacher_id: str) -> List[Dict[str, Any]]:
        return [course for course in self._courses if course["teacher_id"] == teacher_id]

    async def get_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        for course in self._courses:
            if course["id"] == course_id:
                return course
        return None

    async def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        new_course = {
            "id": str(uuid.uuid4()),
            "name": course_data.get("name"),
            "description": course_data.get("description"),
            "credits": course_data.get("credits"),
            "teacher_id": course_data.get("teacher_id")
        }
        self._courses.append(new_course)
        return new_course

    async def delete_course(self, course_id: str) -> bool:
        for i, course in enumerate(self._courses):
            if course["id"] == course_id:
                del self._courses[i]
                return True
        return False
