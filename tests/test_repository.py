import pytest
from sqlalchemy.exc import IntegrityError

from src.core.repositories.graph import GraphRepository
from src.shemas import Node, Edge


@pytest.mark.asyncio
async def test_create_and_read(db_session):
    repo = GraphRepository(db_session)
    gid = await repo.create_graph(
        [Node(name="A"), Node(name="B")],
        [Edge(source="A", target="B")],
    )
    nodes, edges = await repo.get_graph(gid)
    assert {n.name for n in nodes} == {"A", "B"}
    assert (edges[0].source, edges[0].target) == ("A", "B")

@pytest.mark.asyncio
async def test_unique_vertices(db_session):
    repo = GraphRepository(db_session)
    with pytest.raises(IntegrityError):
        await repo.create_graph(
            [Node(name="A"), Node(name="A")],
            [],
        )

@pytest.mark.asyncio
async def test_adjacency_and_reverse(db_session):
    repo = GraphRepository(db_session)
    gid = await repo.create_graph(
        [Node(name="A"), Node(name="B"), Node(name="C")],
        [Edge(source="A", target="B"), Edge(source="A", target="C"), Edge(source="B", target="C")],
    )
    adj = await repo.adjacency(gid)
    assert adj == {
        "A": ["B", "C"],
        "B": ["C"],
        "C": [],
    }
    rev = await repo.adjacency(gid, reverse=True)
    assert rev == {
        "A": [],
        "B": ["A"],
        "C": ["A", "B"],
    }

@pytest.mark.asyncio
async def test_delete_node_and_cascade(db_session):
    repo = GraphRepository(db_session)
    gid = await repo.create_graph(
        [Node(name="X"), Node(name="Y")],
        [Edge(source="X", target="Y")],
    )
    await repo.delete_node(gid, "X")
    nodes, edges = await repo.get_graph(gid)
    assert {n.name for n in nodes} == {"Y"}
    assert edges == []
    with pytest.raises(KeyError):
        await repo.delete_node(gid, "Z")
