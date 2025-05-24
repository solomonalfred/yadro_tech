from __future__ import annotations
from collections import defaultdict
from itertools import chain
from typing import Dict, List
from sqlalchemy import select, or_ ,delete
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
        node_rows = await self.session.scalars(
            select(Node.id, Node.name).where(Node.graph_id == graph_id)
        )
        nodes = node_rows.all()
        return {n_id: name for n_id, name in nodes}

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
        id_to_name = {n.id: n.name for n in nodes}
        if not nodes:
            return [], []
        edges = await self.session.scalars(
            select(Edge).where(Edge.graph_id == graph_id)
        )
        edges = [
            e for e in edges
            if e.source_id in id_to_name and e.target_id in id_to_name
        ]
        node_dtos = [NodeDTO(name=n.name) for n in nodes]
        id_to_name = {n.id: n.name for n in nodes}
        edge_dtos = [
            EdgeDTO(
                source = id_to_name[e.source_id],
                target = id_to_name[e.target_id],
            )
            for e in edges
        ]
        return node_dtos, edge_dtos

    async def adjacency(self, graph_id: int, reverse: bool = False) -> Dict[str, List[str]]:
        node_rows = await self.session.scalars(
            select(Node).where(Node.graph_id == graph_id)
        )
        nodes = node_rows.all()
        if not nodes:
            raise KeyError("Graph not found")
        id_to_name = {n.id: n.name for n in nodes}
        if not reverse:
            col_a, col_b = Edge.source_id, Edge.target_id
        else:
            col_a, col_b = Edge.target_id, Edge.source_id
        stmt = select(col_a, col_b).where(
            Edge.graph_id == graph_id,
            col_a.in_(id_to_name.keys()),
            col_b.in_(id_to_name.keys()),
        )
        result = await self.session.execute(stmt)
        adj: Dict[str, List[str]] = defaultdict(list)
        for a_id, b_id in result:
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
            raise KeyError("node not found")
        await self.session.execute(
            delete(Edge).where(
                Edge.graph_id == graph_id,
                or_(
                    Edge.source_id == node.id,
                    Edge.target_id == node.id,
                )
            )
        )
        await self.session.delete(node)
        await self.session.commit()
