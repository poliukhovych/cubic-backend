from typing import Optional, Union, Literal
from uuid import UUID
from pydantic import BaseModel, Field
from app.utils.unset import UNSET


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    size: int = Field(..., gt=0, description="Group size (number of students)")
    type: Literal["bachelor", "master"] = Field(..., description="Group type (bachelor or master)")
    course: int = Field(..., ge=1, le=6, description="Course number (1-6)")


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Union[str, None, object] = Field(UNSET, min_length=1, max_length=100)
    size: Union[int, None, object] = Field(UNSET, gt=0)
    type: Union[Literal["bachelor", "master"], None, object] = Field(UNSET)
    course: Union[int, None, object] = Field(UNSET, ge=1, le=6)


class GroupResponse(GroupBase):
    group_id: UUID = Field(..., alias="groupId", description="Unique group identifier")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GroupListResponse(BaseModel):
    groups: list[GroupResponse]
    total: int
