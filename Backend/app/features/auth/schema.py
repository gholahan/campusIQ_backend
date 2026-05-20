import uuid
from pydantic import BaseModel
from app.common.enums import UserRole


class SyncUserRequest(BaseModel):
    role: UserRole
    first_name: str | None = None
    last_name: str | None = None

class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    onboarding_complete: bool