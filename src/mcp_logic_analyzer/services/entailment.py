from __future__ import annotations

from mcp_logic_analyzer.adapters.sympy_adapter import counterexample_model, truth_table_counterexample
from mcp_logic_analyzer.adapters.z3_adapter import finite_countermodel
from mcp_logic_analyzer.models.schemas import CheckEntailmentOutput, CounterexampleOutput, FormalizationSummary
from mcp_logic_analyzer.services.formalizer import parse_logic


def check_entailment(premises: list[str], conclusion: str, logic_family: str) -> CheckEntailmentOutput:
    parsed_premises = [parse_logic(text, logic_family, return_alternatives=False) for text in premises]
    parsed_conclusion = parse_logic(conclusion, logic_family, return_alternatives=False)
    if not parsed_conclusion.candidates or any(not item.candidates for item in parsed_premises):
        return CheckEntailmentOutput(
            status="error",
            logic_family=logic_family,
            entailed=False,
            explanation="Nao foi possivel formalizar todas as sentencas.",
            warnings=["Revise a linguagem natural ou simplifique o argumento."],
        )

    premise_candidates = [item.candidates[0] for item in parsed_premises]
    conclusion_candidate = parsed_conclusion.candidates[0]
    premise_asts = [candidate.ast for candidate in premise_candidates]
    conclusion_ast = conclusion_candidate.ast

    if logic_family == "propositional":
        countermodel = counterexample_model(premise_asts, conclusion_ast) or truth_table_counterexample(premise_asts, conclusion_ast)
        entailed = countermodel is None
        return CheckEntailmentOutput(
            status="ok",
            logic_family=logic_family,
            entailed=entailed,
            proof_sketch=_proof_sketch(premise_candidates, conclusion_candidate) if entailed else None,
            formalization=FormalizationSummary(
                premises=[candidate.surface_form for candidate in premise_candidates],
                conclusion=conclusion_candidate.surface_form,
            ),
            counterexample=countermodel,
            confidence=min([candidate.confidence for candidate in premise_candidates] + [conclusion_candidate.confidence]),
            assumptions=_collect_notes(premise_candidates + [conclusion_candidate]),
            explanation="As premissas implicam a conclusao." if entailed else "Foi encontrada uma valoracao em que as premissas sao verdadeiras e a conclusao e falsa.",
        )

    countermodel = finite_countermodel(premise_asts, conclusion_ast)
    entailed = countermodel is None
    return CheckEntailmentOutput(
        status="ok",
        logic_family=logic_family,
        entailed=entailed,
        proof_sketch="Instanciacao universal seguida de inferencia direta." if entailed else None,
        formalization=FormalizationSummary(
            premises=[candidate.surface_form for candidate in premise_candidates],
            conclusion=conclusion_candidate.surface_form,
        ),
        counterexample=countermodel,
        confidence=min([candidate.confidence for candidate in premise_candidates] + [conclusion_candidate.confidence]),
        assumptions=_collect_notes(premise_candidates + [conclusion_candidate]),
        explanation="Nenhum contraexemplo finito pequeno foi encontrado." if entailed else "Foi encontrado um contraexemplo em um modelo finito simples.",
    )


def find_counterexample(premises: list[str], conclusion: str, logic_family: str) -> CounterexampleOutput:
    result = check_entailment(premises, conclusion, logic_family)
    return CounterexampleOutput(
        status=result.status,
        logic_family=result.logic_family,
        confidence=result.confidence,
        assumptions=result.assumptions,
        ambiguities=result.ambiguities,
        warnings=result.warnings,
        explanation=result.explanation,
        found=result.counterexample is not None,
        counterexample=result.counterexample,
        formalization=result.formalization,
    )


def _proof_sketch(premises, conclusion) -> str:
    rendered = [candidate.surface_form for candidate in premises]
    if len(rendered) >= 2 and any("->" in item for item in rendered):
        return "Modus ponens ou encadeamento proposicional simples."
    return "Verificacao por tabela-verdade/solver."


def _collect_notes(candidates) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        for note in candidate.notes:
            if note not in seen:
                seen.add(note)
                ordered.append(note)
    return ordered
