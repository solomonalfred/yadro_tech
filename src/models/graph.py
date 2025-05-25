from datetime import datetime
from typing import List
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Graph(Base):
    __tablename__ = "graphs"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    nodes: Mapped[List["Node"]] = relationship(
        back_populates="graph", cascade="all, delete-orphan"
    )
    edges: Mapped[List["Edge"]] = relationship(
        back_populates="graph", cascade="all, delete-orphan"
    )


class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = (
        UniqueConstraint("graph_id", "name", name="uq_node_graph_name"),
    )

    graph_id: Mapped[int] = mapped_column(
        ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    graph: Mapped["Graph"] = relationship(back_populates="nodes")


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (
        UniqueConstraint(
            "graph_id", "source_id", "target_id", name="uq_edge_unique"
        ),
    )

    graph_id: Mapped[int] = mapped_column(
        ForeignKey("graphs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False
    )
    graph: Mapped["Graph"] = relationship(back_populates="edges")
