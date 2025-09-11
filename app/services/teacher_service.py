from typing import List, Optional, Dict, Any


class TeacherService:
    def __init__(self):
        self._teachers = [
            {
                "id": "t1",
                "name": "Іван Петрович Коваленко",
                "email": "i.kovalenko@university.edu",
                "department": "Комп'ютерні науки",
                "bio": "Доцент кафедри комп'ютерних наук, спеціалізується на алгоритмах та структурах даних."
            },
            {
                "id": "t2",
                "name": "Марія Олександрівна Сидоренко",
                "email": "m.sydorenko@university.edu",
                "department": "Математика",
                "bio": "Професор кафедри математики, досліджує диференціальні рівняння."
            },
            {
                "id": "t3",
                "name": "Олексій Володимирович Мельник",
                "email": "a.melnyk@university.edu",
                "department": "Фізика",
                "bio": "Доцент кафедри фізики, спеціалізується на квантовій механіці."
            },
            {
                "id": "t4",
                "name": "Анна Сергіївна Бондаренко",
                "email": "a.bondarenko@university.edu",
                "department": "Комп'ютерні науки",
                "bio": "Старший викладач, спеціалізується на веб-розробці та базах даних."
            }
        ]

    async def get_all_teachers(self) -> List[Dict[str, Any]]:
        return self._teachers

    async def get_teacher_by_id(self, teacher_id: str) -> Optional[Dict[str, Any]]:
        for teacher in self._teachers:
            if teacher["id"] == teacher_id:
                return teacher
        return None
