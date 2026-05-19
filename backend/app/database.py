from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    from app import models  # noqa: F401
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Add project_type column if missing
        try:
            await conn.execute(text("ALTER TABLE projects ADD COLUMN project_type VARCHAR(50) DEFAULT 'scrum'"))
        except Exception:
            pass
            
        # Add category column if missing
        try:
            await conn.execute(text("ALTER TABLE projects ADD COLUMN category VARCHAR(100) DEFAULT 'Software'"))
        except Exception:
            pass
            
        # Add url column if missing
        try:
            await conn.execute(text("ALTER TABLE projects ADD COLUMN url VARCHAR(255)"))
        except Exception:
            pass
