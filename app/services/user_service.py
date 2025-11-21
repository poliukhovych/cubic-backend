from typing import Optional
import uuid

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserListResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self._repository = repo

    async def get_all_users(self) -> UserListResponse:
        users = await self._repository.find_all()
        total = len(users)
        return UserListResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total=total
        )

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserResponse]:
        user = await self._repository.find_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None

