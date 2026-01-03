from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import engine

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
