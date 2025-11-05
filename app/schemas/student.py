import uuid

from pydantic import BaseModel, ConfigDict


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: uuid.UUID
    first_name: str
    last_name: str
    patronymic: str | None = None
    confirmed: bool
