from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


NodeType = Literal[
    "atom",
    "predicate",
    "not",
    "and",
    "or",
    "implies",
    "iff",
    "forall",
    "exists",
]


class LogicalNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: NodeType
    name: str | None = None
    args: list[str] = Field(default_factory=list)
    value: bool | None = None
    left: "LogicalNode | None" = None
    right: "LogicalNode | None" = None
    body: "LogicalNode | None" = None
    var: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def render(self) -> str:
        if self.type == "atom":
            return self.name or "?"
        if self.type == "predicate":
            args = ", ".join(self.args)
            return f"{self.name}({args})"
        if self.type == "not":
            return f"~{_wrap_unary(self.body)}"
        if self.type == "and":
            return f"({_render_pair(self.left)} & {_render_pair(self.right)})"
        if self.type == "or":
            return f"({_render_pair(self.left)} | {_render_pair(self.right)})"
        if self.type == "implies":
            return f"({_render_pair(self.left)} -> {_render_pair(self.right)})"
        if self.type == "iff":
            return f"({_render_pair(self.left)} <-> {_render_pair(self.right)})"
        if self.type == "forall":
            return f"forall {self.var}. {_render_body(self.body)}"
        if self.type == "exists":
            return f"exists {self.var}. {_render_body(self.body)}"
        raise ValueError(f"Unsupported node type: {self.type}")


def _render_pair(node: LogicalNode | None) -> str:
    return node.render() if node else "?"


def _render_body(node: LogicalNode | None) -> str:
    if node is None:
        return "?"
    rendered = node.render()
    return rendered if rendered.startswith("(") else f"({rendered})"


def _wrap_unary(node: LogicalNode | None) -> str:
    if node is None:
        return "?"
    rendered = node.render()
    if node.type in {"atom", "predicate"}:
        return rendered
    return f"({rendered})"


def atom(name: str) -> LogicalNode:
    return LogicalNode(type="atom", name=name)


def predicate(name: str, *args: str) -> LogicalNode:
    return LogicalNode(type="predicate", name=name, args=list(args))


def negate(body: LogicalNode) -> LogicalNode:
    return LogicalNode(type="not", body=body)


def binary(node_type: Literal["and", "or", "implies", "iff"], left: LogicalNode, right: LogicalNode) -> LogicalNode:
    return LogicalNode(type=node_type, left=left, right=right)


def quantify(node_type: Literal["forall", "exists"], var: str, body: LogicalNode) -> LogicalNode:
    return LogicalNode(type=node_type, var=var, body=body)


LogicalNode.model_rebuild()
