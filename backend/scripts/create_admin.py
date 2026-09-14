import asyncio

from app.core.database import AsyncSessionLocal
from app.infrastructure.auth.password import hash_password
from app.infrastructure.db.models.organization import Organization
from app.infrastructure.db.models.user import User
from sqlalchemy import select


async def main():
    async with AsyncSessionLocal() as session:
        # check existing
        stmt = select(User).where(User.email == "admin@example.com")
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            print("Admin user already exists: admin@example.com")
            return

        org_stmt = select(Organization).where(Organization.slug == "default")
        org_result = await session.execute(org_stmt)
        org = org_result.scalars().first()
        if org is None:
            org = Organization(name="Default Organization", slug="default")
            session.add(org)
            await session.flush()

        u = User(
            organization_id=org.id,
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password=hash_password("adminpass123"),
            role="administrator",
        )
        session.add(u)
        await session.commit()
        print("Created admin user: admin@example.com / adminpass123")


if __name__ == "__main__":
    asyncio.run(main())
