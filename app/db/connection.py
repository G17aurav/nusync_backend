from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """FastAPI dependency yielding a session; commits on success, rolls back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def connect_db():
    """Verifies DB connectivity. Schema is managed by Alembic migrations, not create_all."""
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    print("Connected to DB.")