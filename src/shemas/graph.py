from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict, constr


NodeName = constr(
    pattern=r"^[A-Za-z]+$",
    max_length=255,
    strict=True,
)

class Node(BaseModel):
    name: NodeName

class Edge(BaseModel):
    source: NodeName
    target: NodeName

class GraphCreate(BaseModel):
    nodes: List[Node] = Field(..., min_length=1)
    edges: List[Edge]

class GraphCreateResponse(BaseModel):
    id: int

class GraphReadResponse(GraphCreateResponse):
    nodes: List[Node]
    edges: List[Edge]

class AdjacencyListResponse(BaseModel):
    adjacency_list: Dict[NodeName, List[NodeName]]

class ErrorResponse(BaseModel):
    message: str

class HTTPValidationError(BaseModel):
    model_config = ConfigDict(extra="allow")
