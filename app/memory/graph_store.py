import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update
from sqlalchemy.dialects.postgresql import insert
from app.db.models import GraphNode, GraphEdge
from app.db.repositories import GraphRepository

logger = structlog.get_logger(__name__)

class GraphStore:
    def __init__(self, session: AsyncSession):
        self.repo = GraphRepository(session)
        self.session = session

    async def add_entity(self, entity_id: str, workspace_id: str, entity_type: str, properties: Dict[str, Any]) -> None:
        """Add a node (entity) to the knowledge graph with proper concurrency handling (UPSERT)."""
        try:
            stmt = insert(GraphNode).values(
                id=entity_id,
                workspace_id=workspace_id,
                type=entity_type,
                properties=properties
            )
            
            # On conflict, update properties
            # This ensures thread safety without needing SELECT FOR UPDATE.
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={'properties': properties, 'type': entity_type}
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info("graph_entity_upserted", entity_id=entity_id)
        except Exception as e:
            await self.session.rollback()
            logger.error("graph_add_entity_error", error=str(e), entity_id=entity_id)

    async def add_relationship(self, source_id: str, target_id: str, workspace_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> None:
        """Add an edge (relationship) to the knowledge graph."""
        try:
            # For simplicity, edge uniqueness isn't enforced strictly here unless we define a composite unique constraint.
            # We assume edges are additive, or we would similarly use an UPSERT.
            await self.repo.add_edge(source_id, target_id, workspace_id, relationship_type, properties or {})
            logger.info("graph_relationship_added", source=source_id, target=target_id, type=relationship_type)
        except Exception as e:
            await self.session.rollback()
            logger.error("graph_add_relationship_error", error=str(e), source=source_id, target=target_id)

    async def get_subgraph(self, workspace_id: str, entity_ids: List[str]) -> Dict[str, Any]:
        """Retrieves nodes and edges connected to the specified entity IDs."""
        try:
            nodes_stmt = select(GraphNode).where(
                GraphNode.workspace_id == workspace_id,
                GraphNode.id.in_(entity_ids)
            )
            nodes_result = await self.session.execute(nodes_stmt)
            nodes = nodes_result.scalars().all()

            edges_stmt = select(GraphEdge).where(
                GraphEdge.workspace_id == workspace_id,
                or_(
                    GraphEdge.source_id.in_(entity_ids),
                    GraphEdge.target_id.in_(entity_ids)
                )
            )
            edges_result = await self.session.execute(edges_stmt)
            edges = edges_result.scalars().all()

            return {
                "nodes": [{"id": n.id, "type": n.type, "properties": n.properties} for n in nodes],
                "edges": [{"source": e.source_id, "target": e.target_id, "type": e.relationship_type, "properties": e.properties} for e in edges]
            }
        except Exception as e:
            logger.error("graph_get_subgraph_error", error=str(e))
            return {"nodes": [], "edges": []}
