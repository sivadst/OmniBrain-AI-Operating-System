import structlog
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, UpdateStatus
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.schemas.memory import DocumentChunk

logger = structlog.get_logger(__name__)

class VectorStore:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.QDRANT_URL)
        # Using a small, fast model for embeddings
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = "omnibrain_memory"

    async def initialize(self):
        """Creates the collection if it doesn't exist."""
        try:
            collections = await self.client.get_collections()
            if not any(c.name == self.collection_name for c in collections.collections):
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
                logger.info("qdrant_collection_created", collection=self.collection_name)
        except Exception as e:
            logger.error("qdrant_init_error", error=str(e))
            raise

    async def upsert_chunks(self, chunks: List[DocumentChunk]):
        """Upsert memory chunks into Qdrant."""
        points = [
            PointStruct(
                id=chunk.id,
                vector=chunk.embedding,
                payload={"content": chunk.content, **chunk.metadata}
            )
            for chunk in chunks
        ]
        
        try:
            result = await self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=points
            )
            if result.status != UpdateStatus.COMPLETED:
                logger.warning("qdrant_upsert_incomplete", status=result.status)
            else:
                logger.info("qdrant_upsert_success", count=len(chunks))
        except Exception as e:
            logger.error("qdrant_upsert_error", error=str(e))
            raise

    async def search(self, query: str, limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Dense vector search using the encoded query."""
        try:
            query_vector = self.encoder.encode(query).tolist()
            
            # Simple metadata filtering if provided
            # For complex filters, we would map filter_dict to Qdrant Filter objects
            
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "id": str(res.id),
                    "score": res.score,
                    "content": res.payload.get("content", "") if res.payload else "",
                    "metadata": {k: v for k, v in res.payload.items() if k != "content"} if res.payload else {}
                }
                for res in results
            ]
        except Exception as e:
            logger.error("qdrant_search_error", error=str(e), query=query)
            return []

    def generate_embedding(self, text: str) -> List[float]:
        return self.encoder.encode(text).tolist()
