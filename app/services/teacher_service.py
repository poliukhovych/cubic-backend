from typing import Optional
import uuid

from app.repositories.teacher_repository import TeacherRepository
from app.repositories.user_repository import UserRepository
from app.core.exceptions import ConflictError
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse


class TeacherService:
    def __init__(self, repo: TeacherRepository, user_repo: Optional[UserRepository] = None):
        self._repository = repo
        self._user_repository = user_repo

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
            status=teacher_data.status,
            user_id=teacher_data.user_id
        )

        return TeacherResponse.model_validate(teacher)

    async def update_teacher(self, teacher_id: uuid.UUID, teacher_data: TeacherUpdate) -> Optional[TeacherResponse]:
        teacher = await self._repository.update(
            teacher_id=teacher_id,
            first_name=teacher_data.first_name,
            last_name=teacher_data.last_name,
            patronymic=teacher_data.patronymic,
            status=teacher_data.status,
            user_id=teacher_data.user_id
        )

        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    async def delete_teacher(self, teacher_id: uuid.UUID) -> bool:
        teacher = await self._repository.find_by_id(teacher_id)
        if not teacher:
            return False
        if await self._repository.has_assignments(teacher_id):
            raise ConflictError(
                "Викладач є в збережених розкладах. Спочатку видаліть або перегенеруйте ці розклади."
            )
        user_id = teacher.user_id
        deleted = await self._repository.delete(teacher_id)
        if deleted and user_id and self._user_repository:
            await self._user_repository.delete_account(user_id)
        return deleted

    async def activate_teacher(self, teacher_id: uuid.UUID) -> Optional[TeacherResponse]:
        teacher = await self._repository.activate_teacher(teacher_id)
        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    async def deactivate_teacher(self, teacher_id: uuid.UUID) -> Optional[TeacherResponse]:
        teacher = await self._repository.deactivate_teacher(teacher_id)
        if teacher:
            return TeacherResponse.model_validate(teacher)
        return None

    def get_full_name(self, teacher) -> str:
        return f"{teacher.last_name} {teacher.first_name} {teacher.patronymic}"
