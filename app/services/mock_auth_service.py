import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from jose import JWTError, jwt

from app.db.models.user import UserRole, UserStatus

logger = logging.getLogger(__name__)

SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class MockAuthService:
    
    def __init__(self):
        self.mock_users = {
            "dev-admin": {
                "id": str(uuid4()),
                "name": "Dev Admin",
                "email": "admin@dev.local",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "google_id": "dev-admin",
                "avatar_url": None,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "is_verified": True
            },
            "dev-teacher": {
                "id": str(uuid4()),
                "name": "Dev Teacher",
                "email": "teacher@dev.local",
                "role": UserRole.TEACHER,
                "status": UserStatus.ACTIVE,
                "google_id": "dev-teacher",
                "avatar_url": None,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "is_verified": True
            },
            "dev-student": {
                "id": str(uuid4()),
                "name": "Dev Student",
                "email": "student@dev.local",
                "role": UserRole.STUDENT,
                "status": UserStatus.ACTIVE,
                "google_id": "dev-student",
                "avatar_url": None,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "is_verified": True
            }
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        for user in self.mock_users.values():
            if user["id"] == user_id:
                return user
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for user in self.mock_users.values():
            if user["email"] == email:
                return user
        return None
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        return self.mock_users.get(google_id)
    
    async def create_or_update_user(
        self,
        google_id: str,
        name: str,
        email: str,
        avatar_url: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None
    ) -> Dict[str, Any]:
        user = self.mock_users.get(google_id)
        
        if user:
            user.update({
                "name": name,
                "email": email,
                "avatar_url": avatar_url,
                "last_login": datetime.utcnow()
            })
            if role:
                user["role"] = role
            if status:
                user["status"] = status
        else:
            user = {
                "id": str(uuid4()),
                "name": name,
                "email": email,
                "role": role or UserRole.STUDENT,
                "status": status or UserStatus.ACTIVE,
                "google_id": google_id,
                "avatar_url": avatar_url,
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                "is_active": True,
                "is_verified": True
            }
            self.mock_users[google_id] = user
        
        logger.info(f"Mock user created/updated: {user['email']}")
        return user
    
    def create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
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
        logger.info(f"Mock token revoked: {token[:20]}...")
        return True
