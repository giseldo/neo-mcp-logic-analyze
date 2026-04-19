from __future__ import annotations

from mcp_logic_analyzer.adapters.sympy_adapter import satisfiable_model
from mcp_logic_analyzer.adapters.z3_adapter import finite_model_search, minimal_unsat_core
from mcp_logic_analyzer.models.ast import LogicalNode
from mcp_logic_analyzer.models.schemas import CheckConsistencyOutput, FormalizationSummary
from mcp_logic_analyzer.services.formalizer import parse_logic


def check_consistency(premises: list[str], logic_family: str) -> CheckConsistencyOutput:
    parsed = [parse_logic(text, logic_family, return_alternatives=False) for text in premises]
    candidates = [item.candidates[0] for item in parsed if item.candidates]
    if len(candidates) != len(premises):
        return CheckConsistencyOutput(
            status="error",
            logic_family=logic_family,
            consistent=False,
            reason="Nem todas as premissas puderam ser formalizadas.",
            warnings=["Revise as premissas que nao casaram com os padroes da V1."],
        )

    asts = [candidate.ast for candidate in candidates]
    if logic_family == "propositional":
        model = satisfiable_model(asts)
        consistent = model is not None
        return CheckConsistencyOutput(
            status="ok",
            logic_family=logic_family,
            consistent=consistent,
            reason="Existe ao menos uma valoracao que satisfaz todas as premissas." if consistent else "As premissas sao incompatíveis em todas as valoracoes proposicionais.",
            unsat_core=[] if consistent else list(range(len(premises))),
            counterexample=None if consistent else {},
            formalization=FormalizationSummary(premises=[candidate.surface_form for candidate in candidates]),
            confidence=min(candidate.confidence for candidate in candidates),
            assumptions=_collect_notes(candidates),
        )

    model = finite_model_search(asts)
    contradiction_core = _detect_natural_language_contradiction(asts)
    if contradiction_core:
        model = None
    consistent = model is not None
    return CheckConsistencyOutput(
        status="ok",
        logic_family=logic_family,
        consistent=consistent,
        reason="Foi encontrado um modelo finito simples para as premissas." if consistent else "As premissas expressam regras incompatíveis para a mesma classe e o mesmo predicado na leitura controlada da V1." if contradiction_core else "Nao foi encontrado modelo finito pequeno para satisfazer simultaneamente as premissas.",
        unsat_core=[] if consistent else contradiction_core or minimal_unsat_core(asts),
        counterexample=None if consistent else {},
        formalization=FormalizationSummary(premises=[candidate.surface_form for candidate in candidates]),
        confidence=min(candidate.confidence for candidate in candidates),
        assumptions=_collect_notes(candidates),
    )


def _collect_notes(candidates) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        for note in candidate.notes:
            if note not in seen:
                seen.add(note)
                ordered.append(note)
    return ordered


def _detect_natural_language_contradiction(nodes: list[LogicalNode]) -> list[int]:
    patterns: list[tuple[str, str, bool, int]] = []
    for index, node in enumerate(nodes):
        parsed = _as_universal_rule(node)
        if parsed:
            subject, predicate_name, positive = parsed
            patterns.append((subject, predicate_name, positive, index))

    for subject, predicate_name, positive, index in patterns:
        for other_subject, other_predicate, other_positive, other_index in patterns:
            if index >= other_index:
                continue
            if subject == other_subject and predicate_name == other_predicate and positive != other_positive:
                return [index, other_index]
    return []


def _as_universal_rule(node: LogicalNode) -> tuple[str, str, bool] | None:
    if node.type != "forall" or node.body is None or node.var is None:
        return None
    body = node.body
    if body.type != "implies" or body.left is None or body.right is None:
        return None
    if body.left.type != "predicate" or body.left.args != [node.var]:
        return None
    if body.right.type == "predicate" and body.right.args == [node.var]:
        return (body.left.name or "", body.right.name or "", True)
    if body.right.type == "not" and body.right.body and body.right.body.type == "predicate" and body.right.body.args == [node.var]:
        return (body.left.name or "", body.right.body.name or "", False)
    return None
