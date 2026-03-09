"""
Shared FastAPI dependencies — DB session, settings, etc.
"""

from app.config import Settings, settings


def get_settings() -> Settings:
    """Return the global settings singleton."""
    return settings


# ── Database session (placeholder until Alembic/SA engine is wired) ─────
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# engine = create_async_engine(settings.database_url, echo=False)
# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session() as session:
#         yield session
