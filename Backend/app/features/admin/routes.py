from fastapi import (
    APIRouter,
    Depends,
)
from app.features.auth.dependencies import require_admin
from app.features.users.models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)
@router.get("/welcome")
async def admin_dashboard(
    user:User = Depends(require_admin)
):
    return {"message": "welcome admin"}