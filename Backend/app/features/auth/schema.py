from pydantic import BaseModel
from app.common.enums import UserRole


class SyncUserRequest(BaseModel):
    role: UserRole
    first_name: str
    last_name: str