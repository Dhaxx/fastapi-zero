from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from settings import Settings

settings = Settings()
engine = create_async_engine(settings.DATABASE_URL)


def get_session():
    with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
