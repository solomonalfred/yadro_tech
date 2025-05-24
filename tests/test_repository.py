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
