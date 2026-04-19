from __future__ import annotations

from mcp_logic_analyzer.models.ast import LogicalNode
from mcp_logic_analyzer.models.schemas import ExplainFormalizationOutput
from mcp_logic_analyzer.services.formalizer import parse_logic


def explain_formalization(text: str, logic_family: str) -> ExplainFormalizationOutput:
    parsed = parse_logic(text, logic_family, return_alternatives=True)
    candidate = parsed.candidates[0] if parsed.candidates else None
    if candidate is None:
        return ExplainFormalizationOutput(
            status="error",
            logic_family=logic_family,
            explanation="Nao foi possivel explicar uma formalizacao inexistente.",
            warnings=["O texto nao casou com os padroes implementados na V1."],
        )
    explanation = _explain_node(candidate.ast)
    return ExplainFormalizationOutput(
        status="ok",
        logic_family=logic_family,
        confidence=candidate.confidence,
        assumptions=candidate.notes,
        ambiguities=parsed.ambiguities,
        explanation=explanation,
        candidate=candidate,
    )


def _explain_node(node: LogicalNode) -> str:
    if node.type == "atom":
        return f"A sentenca foi tratada como a proposicao atomica {node.name}."
    if node.type == "predicate":
        args = ", ".join(node.args)
        return f"A formula afirma que o predicado {node.name} vale para {args}."
    if node.type == "not" and node.body:
        return f"A formula nega que: {_explain_node(node.body)}"
    if node.type == "and" and node.left and node.right:
        return f"A formula exige que ambas as partes sejam verdadeiras: {_explain_node(node.left)} e {_explain_node(node.right)}"
    if node.type == "or" and node.left and node.right:
        return f"A formula afirma que pelo menos uma das partes vale: {_explain_node(node.left)} ou {_explain_node(node.right)}"
    if node.type == "implies" and node.left and node.right:
        return f"A formula diz que sempre que {_summarize(node.left)}, entao {_summarize(node.right)}."
    if node.type == "iff" and node.left and node.right:
        return f"A formula expressa equivalencia entre {_summarize(node.left)} e {_summarize(node.right)}."
    if node.type == "forall" and node.var and node.body:
        return f"A formula quantifica universalmente sobre {node.var}: para todo elemento do dominio, {_summarize(node.body)}."
    if node.type == "exists" and node.var and node.body:
        return f"A formula quantifica existencialmente sobre {node.var}: existe pelo menos um elemento tal que {_summarize(node.body)}."
    return f"Formula: {node.render()}"


def _summarize(node: LogicalNode) -> str:
    text = node.render()
    return text[0].lower() + text[1:] if text else text
