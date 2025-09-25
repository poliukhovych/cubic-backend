from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    size: int = Field(..., gt=0, description="Group size (number of students)")


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    size: Optional[int] = Field(None, gt=0)


class GroupResponse(GroupBase):
    group_id: UUID = Field(..., description="Unique group identifier")
    
    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    groups: list[GroupResponse]
    total: int
