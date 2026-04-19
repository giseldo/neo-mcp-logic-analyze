from __future__ import annotations

from mcp_logic_analyzer.models.schemas import AmbiguityReport, DetectAmbiguitiesOutput


def detect_ambiguities(text: str) -> DetectAmbiguitiesOutput:
    reports: list[AmbiguityReport] = []
    lowered = text.lower()

    if " ou " in lowered:
        reports.append(
            AmbiguityReport(
                text=text,
                kind="disjunction",
                message="A palavra 'ou' pode ser inclusiva ou exclusiva em linguagem natural.",
                severity="medium",
                suggestions=[
                    "Explique se uma ou ambas as alternativas podem ser verdadeiras.",
                    "Use 'ou exclusivamente' se quiser exclusao mutua.",
                ],
            )
        )

    if "um " in lowered or "uma " in lowered:
        if any(trigger in lowered for trigger in ["todo ", "toda ", "cada ", "all ", "every "]):
            reports.append(
                AmbiguityReport(
                    text=text,
                    kind="quantifier_scope",
                    message="Ha um padrao potencialmente ambiguo entre quantificador universal e um existencial interno.",
                    severity="high",
                    suggestions=[
                        "Especifique se existe um unico objeto para todos os individuos ou possivelmente objetos diferentes para cada individuo.",
                    ],
                )
            )

    if " nao " in f" {lowered} " and " ou " in lowered:
        reports.append(
            AmbiguityReport(
                text=text,
                kind="negation_scope",
                message="A negacao pode ter escopo sobre apenas uma clausula ou sobre a disjuncao inteira.",
                severity="high",
                suggestions=[
                    "Reescreva usando parenteses em linguagem natural, como 'nao (A ou B)' ou '(nao A) ou B'.",
                ],
            )
        )

    if " com " in lowered:
        reports.append(
            AmbiguityReport(
                text=text,
                kind="attachment",
                message="A expressao preposicional introduzida por 'com' pode modificar mais de um constituinte.",
                severity="medium",
                suggestions=[
                    "Explique quem possui ou usa o instrumento mencionado.",
                ],
            )
        )

    return DetectAmbiguitiesOutput(
        status="ok",
        ambiguities=[report.message for report in reports],
        reports=reports,
        confidence=max(0.35, 1.0 - 0.15 * len(reports)),
        explanation="Ambiguidades relevantes para formalizacao foram identificadas." if reports else "Nenhuma ambiguidade forte detectada pelos padroes da V1.",
    )
