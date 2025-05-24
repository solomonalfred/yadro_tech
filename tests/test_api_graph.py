import pytest
from fastapi import status


GRAPH_URL = "/api/graph"

@pytest.mark.asyncio
async def test_full_graph_lifecycle(client):
    resp = await client.post(
        GRAPH_URL,
        json={
            "nodes": [{"name": "A"}, {"name": "B"}],
            "edges": [{"source": "A", "target": "B"}],
        }, follow_redirects=True
    )
    assert resp.status_code == status.HTTP_201_CREATED
    gid = resp.json()["id"]
    resp = await client.get(f"{GRAPH_URL}/{gid}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["nodes"] == [{"name": "A"}, {"name": "B"}]
    resp = await client.get(f"{GRAPH_URL}/{gid}/adjacency_list")
    assert resp.json()["adjacency_list"]["A"] == ["B"]
    resp = await client.get(f"{GRAPH_URL}/{gid}/reverse_adjacency_list")
    assert resp.json()["adjacency_list"]["B"] == ["A"]
    resp = await client.delete(f"{GRAPH_URL}/{gid}/node/A")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    resp = await client.get(f"{GRAPH_URL}/{gid}/adjacency_list")
    assert "A" not in resp.json()["adjacency_list"]

@pytest.mark.asyncio
async def test_cycle_returns_400(client):
    resp = await client.post(
        GRAPH_URL,
        json={
            "nodes": [{"name": "A"}, {"name": "B"}],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "B", "target": "A"},
            ],
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "cycle" in resp.json()["detail"]
