from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_async_session
from src.core import ensure_dag, GraphRepository
from src.services import (
    GraphService,
    GraphNotFound,
    NodeNotFound,
    InvalidGraph,
)
from src.shemas import (
    AdjacencyListResponse,
    Edge,
    GraphCreate,
    GraphCreateResponse,
    GraphReadResponse,
    Node,
    ErrorResponse
)


router = APIRouter(
    prefix="/api/graph",
    tags=["graph"]
)

async def get_graph_service(db: AsyncSession = Depends(get_async_session),) -> GraphService:
    return GraphService(GraphRepository(db))

@router.post(
    path="",
    response_model=GraphCreateResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_graph_api_graph(
        body: GraphCreate,
        service: GraphService = Depends(get_graph_service),
):
    try:
        gid = await service.create(body)
    except InvalidGraph as err:
        raise HTTPException(status_code=400, detail=str(err))
    return GraphCreateResponse(id=gid)

@router.get(
    "/{graph_id}",
    response_model=GraphReadResponse,
    responses={404: {"model": ErrorResponse}},
)
async def read_graph_api_graph(
    graph_id: int,
    service: GraphService = Depends(get_graph_service)
):
    try:
        return await service.read(graph_id)
    except GraphNotFound as err:
        raise HTTPException(status_code=404, detail=str(err))

@router.get(
    "/{graph_id}/adjacency_list",
    response_model=AdjacencyListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_adjacency_list_api_graph(
    graph_id: int,
    service: GraphService = Depends(get_graph_service)
):
    try:
        adj = await service.adjacency(graph_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
    return adj

@router.get(
    "/{graph_id}/reverse_adjacency_list",
    response_model=AdjacencyListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_reverse_adjacency_list_api_graph(
    graph_id: int,
    service: GraphService = Depends(get_graph_service)
):
    try:
        adj = await service.adjacency(graph_id, reverse=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
    return adj

@router.delete(
    "/{graph_id}/node/{node_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_node_api_graph(
    graph_id: int,
    node_name: str,
    service: GraphService = Depends(get_graph_service)
):
    try:
        await service.delete_node(graph_id, node_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph or node not found")

