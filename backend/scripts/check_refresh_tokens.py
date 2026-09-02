import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.infrastructure.db.models.refresh_token import RefreshToken


async def main():
    async with AsyncSessionLocal() as session:
        stmt = select(RefreshToken)
        res = await session.execute(stmt)
        rows = res.scalars().all()
        for r in rows:
            print(r.id, r.token[:8]+"...", r.user_id, r.revoked)


if __name__ == '__main__':
    asyncio.run(main())
