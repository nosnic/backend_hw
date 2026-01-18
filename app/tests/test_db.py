import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, Item

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # для тестов in-memory

@pytest.mark.asyncio
async def test_create_item_in_db():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        item = Item(name="TestItem")
        session.add(item)
        await session.commit()
        await session.refresh(item)
        assert item.id is not None
        assert item.name == "TestItem"
