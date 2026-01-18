import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_item_endpoint(monkeypatch):
    async def fake_publish(*args, **kwargs):
        return True
    # патчим aio_pika.publish чтобы не требовался реальный RabbitMQ
    monkeypatch.setattr("app.main.channel.default_exchange.publish", fake_publish)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/items/", json={"name": "TestEndpoint"})
    assert response.status_code == 200
    assert response.json()["name"] == "TestEndpoint"
