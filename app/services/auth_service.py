import logging
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.db.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserCreate, UserUpdate
from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = getattr(settings, 'SECRET_KEY', 'dev-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        try:
            result = await self.db.execute(
                select(User).where(User.google_id == google_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by Google ID {google_id}: {str(e)}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        try:
            user = User(
                name=user_data.name,
                email=user_data.email,
                role=user_data.role,
                status=user_data.status,
                google_id=user_data.google_id,
                avatar_url=user_data.avatar_url
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Created new user: {user.email}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        try:
            update_data = user_data.model_dump(exclude_unset=True)
            
            if not update_data:
                return await self.get_user_by_id(user_id)
            
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data, updated_at=datetime.utcnow())
            )
            await self.db.commit()
            
            return await self.get_user_by_id(user_id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    async def create_or_update_user(
        self,
        google_id: str,
        name: str,
        email: str,
        avatar_url: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None
    ) -> User:
        try:
            user = await self.get_user_by_google_id(google_id)
            
            if user:
                update_data = {
                    "name": name,
                    "email": email,
                    "avatar_url": avatar_url,
                    "last_login": datetime.utcnow()
                }
                
                if role:
                    update_data["role"] = role
                if status:
                    update_data["status"] = status
                
                await self.db.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(**update_data, updated_at=datetime.utcnow())
                )
                await self.db.commit()
                await self.db.refresh(user)
                
                logger.info(f"Updated existing user: {user.email}")
                return user
            else:
                existing_user = await self.get_user_by_email(email)
                
                if existing_user:
                    await self.db.execute(
                        update(User)
                        .where(User.id == existing_user.id)
                        .values(
                            google_id=google_id,
                            name=name,
                            avatar_url=avatar_url,
                            last_login=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    await self.db.commit()
                    await self.db.refresh(existing_user)
                    
                    logger.info(f"Linked existing user with Google: {existing_user.email}")
                    return existing_user
                else:
                    user = User(
                        google_id=google_id,
                        name=name,
                        email=email,
                        avatar_url=avatar_url,
                        role=role or UserRole.STUDENT,
                        status=status or UserStatus.PENDING_PROFILE
                    )
                    
                    self.db.add(user)
                    await self.db.commit()
                    await self.db.refresh(user)
                    
                    logger.info(f"Created new user via Google: {user.email}")
                    return user
                    
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating/updating user: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
        return self.create_access_token(user_id, expires_delta)
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                return None
            
            return {
                "id": user_id,
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        # TODO: Реалізувати чорний список токенів (Redis або база даних)
        logger.info(f"Token revoked: {token[:20]}...")
        return True
