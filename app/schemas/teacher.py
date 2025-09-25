from typing import Optional
import uuid
from pydantic import BaseModel, Field


class TeacherBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Ім'я")
    last_name: str = Field(..., min_length=1, max_length=100, description="Прізвище")
    patronymic: str = Field(..., min_length=1, max_length=100, description="По батькові")
    confirmed: bool = Field(default=False, description="Чи підтверджений викладач")


class TeacherCreate(TeacherBase):
    user_id: Optional[uuid.UUID] = Field(None, description="ID користувача (опціонально)")


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Ім'я")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Прізвище")
    patronymic: Optional[str] = Field(None, min_length=1, max_length=100, description="По батькові")
    confirmed: Optional[bool] = Field(None, description="Чи підтверджений викладач")
    user_id: Optional[uuid.UUID] = Field(None, description="ID користувача")


class TeacherResponse(TeacherBase):
    teacher_id: uuid.UUID = Field(..., description="ID викладача")
    user_id: Optional[uuid.UUID] = Field(None, description="ID користувача")

    class Config:
        from_attributes = True


class TeacherListResponse(BaseModel):
    teachers: list[TeacherResponse] = Field(..., description="Список викладачів")
    total: int = Field(..., description="Загальна кількість викладачів")
