import pytest
import asyncio
from app.consumer import main as consumer_main

@pytest.mark.asyncio
async def test_consumer_runs(monkeypatch):
    async def fake_connect_robust(*args, **kwargs):
        class DummyConnection:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc, tb): return False
            async def channel(self):
                class DummyChannel:
                    async def declare_queue(self, name):
                        class DummyQueue:
                            async def __aenter__(self): return self
                            async def __aexit__(self, exc_type, exc, tb): pass
                            async def iterator(self):
                                class DummyIter:
                                    async def __aiter__(self):
                                        return self
                                    async def __anext__(self):
                                        raise StopAsyncIteration
                                return DummyIter()
                        return DummyQueue()
                return DummyChannel()
        return DummyConnection()
    monkeypatch.setattr("aio_pika.connect_robust", fake_connect_robust)
    await consumer_main()
