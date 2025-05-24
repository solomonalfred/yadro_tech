from __future__ import annotations
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import ensure_dag, GraphRepository
from src.shemas import (
    AdjacencyListResponse,
    Edge,
    GraphCreate,
    GraphReadResponse,
    Node,
)


class GraphServiceError(Exception):
    pass

class GraphNotFound(GraphServiceError):
    pass

class NodeNotFound(GraphServiceError):
    pass

class InvalidGraph(GraphServiceError):
    pass

class GraphService:
    def __init__(self, graph: GraphRepository) -> None:
        self._repo = graph

    async def create(self, payload: GraphCreate) -> int:
        try:
            ensure_dag(payload.nodes, payload.edges)
        except ValueError as e:
            raise InvalidGraph(str(e))
        try:
            return await self._repo.create_graph(payload.nodes, payload.edges)
        except Exception as e:
            raise InvalidGraph(str(e))

    async def read(self, graph_id: int) -> GraphReadResponse:
        nodes, edges = await self._repo.get_graph(graph_id)
        if not nodes:
            raise GraphNotFound(f"Graph {graph_id} not found")
        return GraphReadResponse(id=graph_id, nodes=nodes, edges=edges)

    async def adjacency(self, graph_id: int, *, reverse: bool = False) -> AdjacencyListResponse:
        try:
            adj = await self._repo.adjacency(graph_id, reverse=reverse)
        except KeyError:
            raise GraphNotFound(f"Graph {graph_id} not found")
        return AdjacencyListResponse(adjacency_list=adj)

    async def delete_node(self, graph_id: int, node_name: str) -> None:
        try:
            await self._repo.delete_node(graph_id, node_name)
        except KeyError:
            raise NodeNotFound(f"Node '{node_name}' not found in graph {graph_id}")
