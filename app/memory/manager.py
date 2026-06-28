import structlog
from typing import Dict, Any, List
from app.memory.vector_store import VectorStore
from app.memory.graph_store import GraphStore

logger = structlog.get_logger(__name__)

class MemoryManager:
    """Facade for interacting with both episodic (Vector) and semantic (Graph) memory."""
    
    def __init__(self, vector_store: VectorStore, graph_store: GraphStore):
        self.vector_store = vector_store
        self.graph_store = graph_store

    async def recall(self, workspace_id: str, query: str) -> str:
        """Searches vector store for episodic memory and pulls related subgraph context."""
        logger.info("memory_recall_start", query=query)
        
        # 1. Search Episodic Memory (Vector DB)
        vector_results = await self.vector_store.search(query, limit=3)
        
        # 2. Extract potential entity IDs from vector metadata to fetch graph context
        entity_ids = set()
        for res in vector_results:
            if "entity_ids" in res["metadata"]:
                entity_ids.update(res["metadata"]["entity_ids"])
                
        # 3. Retrieve Semantic Memory (Graph DB) if entities found
        graph_context = ""
        if entity_ids:
            subgraph = await self.graph_store.get_subgraph(workspace_id, list(entity_ids))
            if subgraph["nodes"] or subgraph["edges"]:
                graph_context = self._format_graph(subgraph)

        # 4. Format combined context
        episodic_context = "\n".join([f"- {res['content']} (Score: {res['score']:.2f})" for res in vector_results])
        
        final_context = "### Episodic Memory (Past Actions & Docs):\n"
        final_context += episodic_context if episodic_context else "No relevant past episodes found.\n"
        
        if graph_context:
            final_context += "\n### Semantic Memory (Knowledge Graph):\n"
            final_context += graph_context
            
        logger.info("memory_recall_complete")
        return final_context

    def _format_graph(self, subgraph: Dict[str, Any]) -> str:
        lines = ["Entities:"]
        for node in subgraph["nodes"]:
            lines.append(f"  - {node['id']} ({node['type']}): {node['properties']}")
        lines.append("Relationships:")
        for edge in subgraph["edges"]:
            lines.append(f"  - {edge['source']} -[{edge['type']}]-> {edge['target']} {edge['properties']}")
        return "\n".join(lines)
