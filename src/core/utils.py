from collections import defaultdict, deque

from src.shemas import Node, Edge


def ensure_dag(nodes: list[Node], edges: list[Edge]) -> None:
    names = {n.name for n in nodes}
    if len(names) != len(nodes):
        raise ValueError("Duplicate node names")
    adj: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = {name: 0 for name in names}
    for e in edges:
        if e.source not in names or e.target not in names:
            raise ValueError(f"Edge refers to unknown node: {e}")
        adj[e.source].append(e.target)
        indeg[e.target] += 1
    q = deque([v for v, d in indeg.items() if d == 0])
    visited = 0
    while q:
        v = q.popleft()
        visited += 1
        for u in adj[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                q.append(u)
    if visited != len(nodes):
        raise ValueError("Graph contains at least one cycle")
