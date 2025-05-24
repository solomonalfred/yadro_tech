import pytest

from src.core import ensure_dag
from src.shemas import Node, Edge


def test_valid_dag():
    nodes = [Node(name="A"), Node(name="B")]
    edges = [Edge(source="A", target="B")]
    ensure_dag(nodes, edges)

@pytest.mark.parametrize(
    "edges",
    [
        [Edge(source="A", target="B"), Edge(source="B", target="A")],
        [Edge(source="A", target="A")],
    ],
)
def test_cycle_detected(edges):
    nodes = [Node(name="A"), Node(name="B")]
    with pytest.raises(ValueError):
        ensure_dag(nodes, edges)

def test_unknown_vertex():
    nodes = [Node(name="A")]
    edges = [Edge(source="A", target="B")]
    with pytest.raises(ValueError):
        ensure_dag(nodes, edges)
