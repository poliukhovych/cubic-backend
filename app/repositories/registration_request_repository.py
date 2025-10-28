"""
Repository for managing registration requests
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.people.registration_request import RegistrationRequest, RegistrationStatus
from typing import List, Optional
import uuid


class RegistrationRequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(self, 
        google_sub: str,
        email: str,
        first_name: str,
        last_name: str,
        patronymic: Optional[str],
        requested_role: str
    ) -> RegistrationRequest:
        request = RegistrationRequest(
            google_sub=google_sub,
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            requested_role=requested_role,
            status=RegistrationStatus.PENDING
        )
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_pending_requests(self) -> List[RegistrationRequest]:
        query = select(RegistrationRequest).where(
            RegistrationRequest.status == RegistrationStatus.PENDING
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_request_by_id(self, request_id: uuid.UUID) -> Optional[RegistrationRequest]:
        query = select(RegistrationRequest).where(
            RegistrationRequest.request_id == request_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_request_by_google_sub(self, google_sub: str) -> Optional[RegistrationRequest]:
        query = select(RegistrationRequest).where(
            RegistrationRequest.google_sub == google_sub,
            RegistrationRequest.status == RegistrationStatus.PENDING
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_request_status(
        self,
        request_id: uuid.UUID,
        status: RegistrationStatus,
        processed_by_id: uuid.UUID
    ) -> Optional[RegistrationRequest]:
        request = await self.get_request_by_id(request_id)
        if request:
            request.status = status
            request.processed_by_id = processed_by_id
            await self.session.flush()
        return request