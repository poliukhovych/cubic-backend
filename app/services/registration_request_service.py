"""
Service for managing registration requests
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.registration_request_repository import RegistrationRequestRepository
from app.db.models.people.registration_request import RegistrationRequest, RegistrationStatus
from app.db.models.people.user import User, UserRole
from typing import List, Optional
import uuid


class RegistrationRequestService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RegistrationRequestRepository(session)

    async def create_request(self,
        google_sub: str,
        email: str,
        first_name: str,
        last_name: str,
        patronymic: Optional[str],
        requested_role: str
    ) -> RegistrationRequest:
        return await self.repository.create_request(
            google_sub=google_sub,
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            requested_role=requested_role
        )

    async def get_pending_requests(self) -> List[RegistrationRequest]:
        return await self.repository.get_pending_requests()

    async def get_request_by_google_sub(self, google_sub: str) -> Optional[RegistrationRequest]:
        return await self.repository.get_request_by_google_sub(google_sub)

    async def approve_request(self, request_id: uuid.UUID, admin_id: uuid.UUID) -> Optional[RegistrationRequest]:
        return await self.repository.update_request_status(
            request_id=request_id,
            status=RegistrationStatus.APPROVED,
            processed_by_id=admin_id
        )

    async def reject_request(self, request_id: uuid.UUID, admin_id: uuid.UUID) -> Optional[RegistrationRequest]:
        return await self.repository.update_request_status(
            request_id=request_id,
            status=RegistrationStatus.REJECTED,
            processed_by_id=admin_id
        )