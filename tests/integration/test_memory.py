import pytest
from app.memory.vector_store import VectorStore
from app.schemas.memory import DocumentChunk

@pytest.mark.asyncio
async def test_vector_store_mocked(monkeypatch):
    class MockQdrantClient:
        def __init__(self, *args, **kwargs):
            pass

        async def get_collections(self):
            class ColList:
                collections = []
            return ColList()
            
        async def create_collection(self, **kwargs):
            pass
            
        async def upsert(self, **kwargs):
            class Status:
                status = "completed"
            return Status()
            
        async def search(self, **kwargs):
            class Res:
                id = "123"
                score = 0.95
                payload = {"content": "Test content"}
            return [Res()]

    monkeypatch.setattr("app.memory.vector_store.AsyncQdrantClient", MockQdrantClient)
    
    # Mock UpdateStatus to prevent comparison issues
    class MockUpdateStatus:
        COMPLETED = "completed"
        
    monkeypatch.setattr("app.memory.vector_store.UpdateStatus", MockUpdateStatus)
    
    store = VectorStore()
    await store.initialize()
    
    chunk = DocumentChunk(id="123", content="Test content", metadata={}, embedding=[0.1]*384)
    await store.upsert_chunks([chunk])
    
    results = await store.search("test")
    assert len(results) == 1
    assert results[0]["content"] == "Test content"
