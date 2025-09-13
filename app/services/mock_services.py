import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class MockTeacherService:
    
    def __init__(self):
        self.mock_teachers = [
            {
                "id": str(uuid4()),
                "name": "Іван Петренко",
                "email": "ivan.petrenko@university.edu",
                "department": "Комп'ютерні науки",
                "position": "Доцент",
                "phone": "+380501234567",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "Марія Коваленко",
                "email": "maria.kovalenko@university.edu",
                "department": "Математика",
                "position": "Професор",
                "phone": "+380509876543",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "Олексій Сидоренко",
                "email": "oleksiy.sydorenko@university.edu",
                "department": "Фізика",
                "position": "Старший викладач",
                "phone": "+380501112233",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_all_teachers(self) -> List[Dict[str, Any]]:
        logger.info("Mock: Getting all teachers")
        return self.mock_teachers
    
    async def get_teacher_by_id(self, teacher_id: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Getting teacher by ID {teacher_id}")
        for teacher in self.mock_teachers:
            if teacher["id"] == teacher_id:
                return teacher
        return None
    
    async def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Mock: Creating teacher {teacher_data.get('name')}")
        new_teacher = {
            "id": str(uuid4()),
            "name": teacher_data.get("name", "Новий викладач"),
            "email": teacher_data.get("email", "new@university.edu"),
            "department": teacher_data.get("department", "Невідомий відділ"),
            "position": teacher_data.get("position", "Викладач"),
            "phone": teacher_data.get("phone", ""),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.mock_teachers.append(new_teacher)
        return new_teacher
    
    async def update_teacher(self, teacher_id: str, teacher_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Updating teacher {teacher_id}")
        for i, teacher in enumerate(self.mock_teachers):
            if teacher["id"] == teacher_id:
                self.mock_teachers[i].update(teacher_data)
                self.mock_teachers[i]["updated_at"] = datetime.utcnow().isoformat()
                return self.mock_teachers[i]
        return None
    
    async def delete_teacher(self, teacher_id: str) -> bool:
        logger.info(f"Mock: Deleting teacher {teacher_id}")
        for i, teacher in enumerate(self.mock_teachers):
            if teacher["id"] == teacher_id:
                del self.mock_teachers[i]
                return True
        return False


class MockCourseService:
    
    def __init__(self):
        self.mock_courses = [
            {
                "id": str(uuid4()),
                "name": "Основи програмування",
                "code": "CS101",
                "description": "Вступ до програмування на Python",
                "credits": 3,
                "teacher_id": None,   
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "Алгоритми та структури даних",
                "code": "CS201",
                "description": "Вивчення основних алгоритмів",
                "credits": 4,
                "teacher_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "Математичний аналіз",
                "code": "MATH101",
                "description": "Основи математичного аналізу",
                "credits": 4,
                "teacher_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_all_courses(self) -> List[Dict[str, Any]]:
        logger.info("Mock: Getting all courses")
        return self.mock_courses
    
    async def get_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Getting course by ID {course_id}")
        for course in self.mock_courses:
            if course["id"] == course_id:
                return course
        return None
    
    async def get_courses_by_teacher_id(self, teacher_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Mock: Getting courses for teacher {teacher_id}")
        return [course for course in self.mock_courses if course.get("teacher_id") == teacher_id]
    
    async def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Mock: Creating course {course_data.get('name')}")
        new_course = {
            "id": str(uuid4()),
            "name": course_data.get("name", "Новий курс"),
            "code": course_data.get("code", "NEW001"),
            "description": course_data.get("description", ""),
            "credits": course_data.get("credits", 3),
            "teacher_id": course_data.get("teacher_id"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.mock_courses.append(new_course)
        return new_course
    
    async def update_course(self, course_id: str, course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Updating course {course_id}")
        for i, course in enumerate(self.mock_courses):
            if course["id"] == course_id:
                self.mock_courses[i].update(course_data)
                self.mock_courses[i]["updated_at"] = datetime.utcnow().isoformat()
                return self.mock_courses[i]
        return None
    
    async def delete_course(self, course_id: str) -> bool:
        logger.info(f"Mock: Deleting course {course_id}")
        for i, course in enumerate(self.mock_courses):
            if course["id"] == course_id:
                del self.mock_courses[i]
                return True
        return False


class MockGroupService:
    
    def __init__(self):
        self.mock_groups = [
            {
                "id": str(uuid4()),
                "name": "КН-21-1",
                "year": 2021,
                "specialty": "Комп'ютерні науки",
                "teacher_id": None,
                "student_count": 25,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "КН-21-2",
                "year": 2021,
                "specialty": "Комп'ютерні науки",
                "teacher_id": None,
                "student_count": 23,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "МАТ-22-1",
                "year": 2022,
                "specialty": "Математика",
                "teacher_id": None,
                "student_count": 20,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
    
    async def get_all_groups(self) -> List[Dict[str, Any]]:
        logger.info("Mock: Getting all groups")
        return self.mock_groups
    
    async def get_group_by_id(self, group_id: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Getting group by ID {group_id}")
        for group in self.mock_groups:
            if group["id"] == group_id:
                return group
        return None
    
    async def get_groups_by_teacher_id(self, teacher_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Mock: Getting groups for teacher {teacher_id}")
        return [group for group in self.mock_groups if group.get("teacher_id") == teacher_id]
    
    async def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Mock: Creating group {group_data.get('name')}")
        new_group = {
            "id": str(uuid4()),
            "name": group_data.get("name", "Нова група"),
            "year": group_data.get("year", 2024),
            "specialty": group_data.get("specialty", "Невідома спеціальність"),
            "teacher_id": group_data.get("teacher_id"),
            "student_count": group_data.get("student_count", 0),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.mock_groups.append(new_group)
        return new_group
    
    async def update_group(self, group_id: str, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Mock: Updating group {group_id}")
        for i, group in enumerate(self.mock_groups):
            if group["id"] == group_id:
                self.mock_groups[i].update(group_data)
                self.mock_groups[i]["updated_at"] = datetime.utcnow().isoformat()
                return self.mock_groups[i]
        return None
    
    async def delete_group(self, group_id: str) -> bool:
        logger.info(f"Mock: Deleting group {group_id}")
        for i, group in enumerate(self.mock_groups):
            if group["id"] == group_id:
                del self.mock_groups[i]
                return True
        return False
