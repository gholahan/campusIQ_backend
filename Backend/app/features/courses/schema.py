import uuid
from pydantic import BaseModel

class CourseRead(BaseModel):
    id: uuid.UUID
    name: str