from typing import Optional
import uuid

from app.repositories.teacher_repository import TeacherRepository
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse


class TeacherService:
    def __init__(self, repo: TeacherRepository):
        self._repository = repo

    async def get_all_teachers(self) -> TeacherListResponse:
        teachers = await self._repository.find_all()
        total = await self._repository.count()
        return TeacherListResponse(
            teachers=[TeacherResponse.model_validate(teacher) for teacher in teachers],
            total=total
        )

    async def get_teacher_by_id(self, teacher_id: uuid.UUID) -> Optional[TeacherResponse]:
        teacher = await self._repository.find_by_id(teacher_id)
        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    async def get_teacher_by_user_id(self, user_id: uuid.UUID) -> Optional[TeacherResponse]:
        teacher = await self._repository.find_by_user_id(user_id)
        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    async def create_teacher(self, teacher_data: TeacherCreate) -> TeacherResponse:
        teacher = await self._repository.create(
            first_name=teacher_data.first_name,
            last_name=teacher_data.last_name,
            patronymic=teacher_data.patronymic,
            confirmed=teacher_data.confirmed,
            user_id=teacher_data.user_id
        )

        return TeacherResponse.model_validate(teacher)

    async def update_teacher(self, teacher_id: uuid.UUID, teacher_data: TeacherUpdate) -> Optional[TeacherResponse]:
        teacher = await self._repository.update(
            teacher_id=teacher_id,
            first_name=teacher_data.first_name,
            last_name=teacher_data.last_name,
            patronymic=teacher_data.patronymic,
            confirmed=teacher_data.confirmed,
            user_id=teacher_data.user_id
        )

        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    async def delete_teacher(self, teacher_id: uuid.UUID) -> bool:
        return await self._repository.delete(teacher_id)

    async def confirm_teacher(self, teacher_id: uuid.UUID) -> Optional[TeacherResponse]:
        teacher = await self._repository.confirm_teacher(teacher_id)
        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    def get_full_name(self, teacher) -> str:
        return f"{teacher.last_name} {teacher.first_name} {teacher.patronymic}"
