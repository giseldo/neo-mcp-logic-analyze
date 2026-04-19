from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from mcp_logic_analyzer.models.ast import LogicalNode


LogicFamily = Literal["propositional", "fol"]


class ToolEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "error"] = "ok"
    logic_family: LogicFamily | None = None
    confidence: float | None = None
    assumptions: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    explanation: str | None = None


class FormalizationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    logic_family: LogicFamily
    surface_form: str
    ast: LogicalNode
    confidence: float = Field(ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)


class ParseLogicInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    logic_family: LogicFamily = "propositional"
    return_alternatives: bool = True


class ParseLogicOutput(ToolEnvelope):
    candidates: list[FormalizationCandidate] = Field(default_factory=list)


class AmbiguityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    kind: str
    message: str
    severity: Literal["low", "medium", "high"] = "medium"
    suggestions: list[str] = Field(default_factory=list)


class DetectAmbiguitiesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    logic_family: LogicFamily | None = None


class DetectAmbiguitiesOutput(ToolEnvelope):
    reports: list[AmbiguityReport] = Field(default_factory=list)


class NormalizeArgumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str


class NormalizeArgumentOutput(ToolEnvelope):
    premises: list[str] = Field(default_factory=list)
    conclusion: str | None = None
    implicit_assumptions: list[str] = Field(default_factory=list)


class FormalizationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premises: list[str] = Field(default_factory=list)
    conclusion: str | None = None


class CheckConsistencyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premises: list[str]
    logic_family: LogicFamily = "propositional"


class CheckConsistencyOutput(ToolEnvelope):
    consistent: bool
    reason: str
    unsat_core: list[int] = Field(default_factory=list)
    formalization: FormalizationSummary | None = None
    counterexample: dict | None = None


class CheckEntailmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premises: list[str]
    conclusion: str
    logic_family: LogicFamily = "propositional"


class CheckEntailmentOutput(ToolEnvelope):
    entailed: bool
    proof_sketch: str | None = None
    formalization: FormalizationSummary | None = None
    counterexample: dict | None = None


class CounterexampleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    premises: list[str]
    conclusion: str
    logic_family: LogicFamily = "propositional"


class CounterexampleOutput(ToolEnvelope):
    found: bool
    counterexample: dict | None = None
    formalization: FormalizationSummary | None = None


class ExplainFormalizationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    logic_family: LogicFamily = "propositional"


class ExplainFormalizationOutput(ToolEnvelope):
    candidate: FormalizationCandidate | None = None
