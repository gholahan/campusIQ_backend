import asyncio

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import engine
from app.core.supabase import supabase_admin
from app.features.users.models import User
from app.features.tutors.models import TutorProfile


async def main():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        users = (await session.exec(select(User))).all()

        for user in users:
            profile = (
                await session.exec(
                    select(TutorProfile).where(TutorProfile.user_id == user.id)
                )
            ).first()

            onboarding_complete = profile is not None

            supabase_admin.auth.admin.update_user_by_id(
                str(user.id),
                {
                    "app_metadata": {
                        "role": user.role,
                        "onboarding_complete": onboarding_complete,
                    }
                },
            )

            print(
                f"✓ {user.id} | {user.role} | onboarded={onboarding_complete}"
            )

    print("Done")


if __name__ == "__main__":
    asyncio.run(main())