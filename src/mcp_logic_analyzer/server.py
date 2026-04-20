from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from mcp_logic_analyzer.config import RESOURCE_ROOT
from mcp_logic_analyzer.models.schemas import (
    CheckConsistencyInput,
    CheckEntailmentInput,
    CounterexampleInput,
    DetectAmbiguitiesInput,
    ExplainFormalizationInput,
    NormalizeArgumentInput,
    ParseLogicInput,
)
from mcp_logic_analyzer.services.ambiguity import detect_ambiguities
from mcp_logic_analyzer.services.consistency import check_consistency
from mcp_logic_analyzer.services.entailment import check_entailment, find_counterexample
from mcp_logic_analyzer.services.explainer import explain_formalization
from mcp_logic_analyzer.services.formalizer import parse_logic
from mcp_logic_analyzer.services.nl_normalizer import normalize_argument


mcp = FastMCP(
    "neo-mcp-logic-analyze",
    instructions=(
        "Servidor MCP para formalizacao controlada de argumentos em linguagem natural, "
        "checagem de consistencia, consequencia logica e geracao de explicacoes auditaveis."
    ),
)


@mcp.tool(name="nl_parse_logic", description="Converte linguagem natural em uma ou mais formalizacoes candidatas.")
def nl_parse_logic(text: str, logic_family: str = "propositional", return_alternatives: bool = True) -> dict:
    payload = ParseLogicInput(text=text, logic_family=logic_family, return_alternatives=return_alternatives)
    return parse_logic(payload.text, payload.logic_family, payload.return_alternatives).model_dump()


@mcp.tool(name="detect_ambiguities", description="Identifica ambiguidades semanticas relevantes para formalizacao.")
def detect_ambiguities_tool(text: str, logic_family: str | None = None) -> dict:
    _ = DetectAmbiguitiesInput(text=text, logic_family=logic_family)
    return detect_ambiguities(text).model_dump()


@mcp.tool(name="check_consistency", description="Verifica se um conjunto de premissas e satisfativel.")
def check_consistency_tool(premises: list[str], logic_family: str = "propositional") -> dict:
    payload = CheckConsistencyInput(premises=premises, logic_family=logic_family)
    return check_consistency(payload.premises, payload.logic_family).model_dump()


@mcp.tool(name="check_entailment", description="Verifica se as premissas implicam a conclusao.")
def check_entailment_tool(premises: list[str], conclusion: str, logic_family: str = "propositional") -> dict:
    payload = CheckEntailmentInput(premises=premises, conclusion=conclusion, logic_family=logic_family)
    return check_entailment(payload.premises, payload.conclusion, payload.logic_family).model_dump()


@mcp.tool(name="find_counterexample", description="Busca um contraexemplo quando a conclusao nao decorre das premissas.")
def find_counterexample_tool(premises: list[str], conclusion: str, logic_family: str = "propositional") -> dict:
    payload = CounterexampleInput(premises=premises, conclusion=conclusion, logic_family=logic_family)
    return find_counterexample(payload.premises, payload.conclusion, payload.logic_family).model_dump()


@mcp.tool(name="explain_formalization", description="Explica a correspondencia entre texto natural e formula logica.")
def explain_formalization_tool(text: str, logic_family: str = "propositional") -> dict:
    payload = ExplainFormalizationInput(text=text, logic_family=logic_family)
    return explain_formalization(payload.text, payload.logic_family).model_dump()


@mcp.tool(name="normalize_argument", description="Separa texto corrido em premissas, conclusao e pressupostos implicitos.")
def normalize_argument_tool(text: str) -> dict:
    payload = NormalizeArgumentInput(text=text)
    return normalize_argument(payload.text).model_dump()


@mcp.resource("logic://schemas/ast-v1", mime_type="application/json")
def ast_schema() -> str:
    return (RESOURCE_ROOT / "ast_schema_v1.json").read_text(encoding="utf-8")


@mcp.resource("logic://examples/propositional", mime_type="application/json")
def examples_propositional() -> str:
    return (RESOURCE_ROOT / "examples_propositional.json").read_text(encoding="utf-8")


@mcp.resource("logic://examples/fol", mime_type="application/json")
def examples_fol() -> str:
    return (RESOURCE_ROOT / "examples_fol.json").read_text(encoding="utf-8")


@mcp.resource("logic://guides/ambiguity-taxonomy", mime_type="text/markdown")
def ambiguity_taxonomy() -> str:
    return (RESOURCE_ROOT / "ambiguity_taxonomy.md").read_text(encoding="utf-8")


@mcp.prompt(name="formalize_argument", description="Prompt guiado para formalizar um argumento em linguagem natural.")
def formalize_argument(argument_text: str) -> str:
    return (
        "Formalize o argumento abaixo usando a AST e a notacao logica do servidor. "
        "Liste premissas, conclusao, suposicoes e ambiguidades antes de propor a formula.\n\n"
        f"Argumento: {argument_text}"
    )


@mcp.prompt(name="teach_logic_step_by_step", description="Prompt didatico para explicar a formalizacao passo a passo.")
def teach_logic_step_by_step(argument_text: str) -> str:
    return (
        "Explique passo a passo como mapear o texto para operadores, quantificadores e predicados. "
        "Use linguagem didatica e aponte onde pode haver perda semantica.\n\n"
        f"Texto: {argument_text}"
    )


@mcp.prompt(name="review_formalization", description="Prompt para revisar uma formalizacao e procurar perdas semanticas.")
def review_formalization(argument_text: str, candidate_json: str = "{}") -> str:
    return (
        "Revise criticamente a formalizacao abaixo. Informe se ha perda semantica, ambiguidades de escopo "
        "ou leituras alternativas plausiveis.\n\n"
        f"Texto original: {argument_text}\n"
        f"Candidata: {candidate_json}"
    )


def main() -> None:
    print("neo-mcp-logic-analyze: servidor MCP iniciado em stdio; aguardando cliente...", file=sys.stderr, flush=True)
    mcp.run()


if __name__ == "__main__":
    main()
