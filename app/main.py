from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
import aio_pika

from .db import get_db, engine, Base
from .models import Item
from .schemas import ItemCreate, ItemRead

app = FastAPI()

# Метрики Prometheus
Instrumentator().instrument(app).expose(app)

# retry для подключения к БД
@app.on_event("startup")
async def startup():
    while True:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception:
            print("PostgreSQL не готов, жду 2 секунды...")
            await asyncio.sleep(2)

@app.post("/items/", response_model=ItemRead)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    new_item = Item(name=item.name)
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # retry для RabbitMQ
    connection = None
    while connection is None:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
        except Exception:
            print("RabbitMQ не готов, жду 2 секунды...")
            await asyncio.sleep(2)

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=f"Item created: {new_item.id}".encode()),
            routing_key="task_queue"
        )
    return new_item
