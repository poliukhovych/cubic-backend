from typing import List, Optional, Dict, Any


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
