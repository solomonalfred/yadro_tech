from __future__ import annotations
from collections import defaultdict
from itertools import chain
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Edge, Graph, Node
from src.shemas import (
    Edge as EdgeDTO,
    Node as NodeDTO
)


class GraphRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _node_map(self, graph_id: int) -> Dict[str, int]:
        result = await self.session.execute(
            select(Node.id, Node.name).where(Node.graph_id == graph_id)
        )
        return {name: _id for _id, name in result.all()}

    async def create_graph(self, nodes: List[NodeDTO], edges: List[EdgeDTO]) -> int:
        graph = Graph()
        self.session.add(graph)
        await self.session.flush()
        node_models = [
            Node(graph_id=graph.id, name=n.name) for n in nodes
        ]
        self.session.add_all(node_models)
        await self.session.flush()
        name_to_id = {m.name: m.id for m in node_models}
        edge_models = [
            Edge(
                graph_id=graph.id,
                source_id=name_to_id[e.source],
                target_id=name_to_id[e.target],
            )
            for e in edges
        ]
        self.session.add_all(edge_models)
        await self.session.commit()
        return graph.id

    async def get_graph(self, graph_id: int) -> tuple[List[NodeDTO], List[EdgeDTO]]:
        nodes = await self.session.scalars(
            select(Node).where(Node.graph_id == graph_id)
        )
        nodes = nodes.all()
        if not nodes:
            return [], []
        edges = await self.session.scalars(
            select(Edge).where(Edge.graph_id == graph_id)
        )
        edges = edges.all()
        node_dtos = [NodeDTO(name=n.name) for n in nodes]
        id_to_name = {n.id: n.name for n in nodes}
        edge_dtos = [
            EdgeDTO(source=id_to_name[e.source_id], target=id_to_name[e.target_id])
            for e in edges
        ]
        return node_dtos, edge_dtos

    async def adjacency(self, graph_id: int, reverse: bool = False) -> Dict[str, List[str]]:
        adj: Dict[str, List[str]] = defaultdict(list)
        stmt = (select(Edge.source_id, Edge.target_id) if not reverse
                else select(Edge.target_id, Edge.source_id)
        ).where(Edge.graph_id == graph_id)
        pairs = await self.session.execute(stmt)
        node_map = await self._node_map(graph_id)
        id_to_name = {v: k for k, v in node_map.items()}
        for a_id, b_id in pairs:
            adj[id_to_name[a_id]].append(id_to_name[b_id])
        for name in id_to_name.values():
            adj.setdefault(name, [])
        for children in adj.values():
            children.sort()
        return dict(adj)

    async def delete_node(self, graph_id: int, node_name: str) -> None:
        result = await self.session.execute(
            select(Node).where(
                Node.graph_id == graph_id, Node.name == node_name
            )
        )
        node = result.scalar_one_or_none()
        if node is None:
            raise KeyError("Node not found")
        await self.session.delete(node)
        await self.session.commit()
