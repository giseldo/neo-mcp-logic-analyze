from __future__ import annotations

import re
from dataclasses import dataclass

from mcp_logic_analyzer.models.ast import LogicalNode, atom, binary, negate, predicate, quantify
from mcp_logic_analyzer.models.schemas import FormalizationCandidate, ParseLogicOutput
from mcp_logic_analyzer.services.ambiguity import detect_ambiguities


@dataclass
class ParseContext:
    symbol_map: dict[str, str]
    assumptions: list[str]
    notes: list[str]


def parse_logic(text: str, logic_family: str, return_alternatives: bool = True) -> ParseLogicOutput:
    ambiguity_output = detect_ambiguities(text)
    normalized_text = _clean_text(text)
    parser = _parse_propositional if logic_family == "propositional" else _parse_fol
    candidates = parser(normalized_text, return_alternatives=return_alternatives)
    confidence = max(candidate.confidence for candidate in candidates) if candidates else 0.0
    return ParseLogicOutput(
        status="ok",
        logic_family=logic_family,
        confidence=confidence,
        assumptions=_merge_unique(note for candidate in candidates for note in candidate.notes),
        ambiguities=ambiguity_output.ambiguities,
        warnings=[] if candidates else ["Nenhuma formalizacao foi produzida."],
        explanation="Foram geradas formalizacoes candidatas controladas a partir do texto." if candidates else "A heuristica atual nao conseguiu formalizar o texto.",
        candidates=candidates,
    )


def _parse_propositional(text: str, return_alternatives: bool) -> list[FormalizationCandidate]:
    context = ParseContext(symbol_map={}, assumptions=[], notes=[])
    primary = _parse_propositional_clause(text, context)
    candidates: list[FormalizationCandidate] = []
    if primary:
        candidates.append(
            FormalizationCandidate(
                logic_family="propositional",
                surface_form=primary.render(),
                ast=primary,
                confidence=_score_propositional(text),
                notes=_build_notes(context),
            )
        )

    if return_alternatives and " ou " in f" {text.lower()} " and primary:
        exclusive = _make_exclusive_or(primary)
        if exclusive:
            candidates.append(
                FormalizationCandidate(
                    logic_family="propositional",
                    surface_form=exclusive.render(),
                    ast=exclusive,
                    confidence=max(0.35, _score_propositional(text) - 0.18),
                    notes=_build_notes(context) + ["Leitura alternativa de 'ou' como disjuncao exclusiva."],
                )
            )
    return candidates


def _parse_fol(text: str, return_alternatives: bool) -> list[FormalizationCandidate]:
    primary, primary_notes = _parse_fol_clause(text)
    candidates: list[FormalizationCandidate] = []
    if primary is not None:
        candidates.append(
            FormalizationCandidate(
                logic_family="fol",
                surface_form=primary.render(),
                ast=primary,
                confidence=_score_fol(text),
                notes=primary_notes,
            )
        )
    if return_alternatives:
        alt = _build_fol_alternative(text)
        if alt:
            node, notes = alt
            candidates.append(
                FormalizationCandidate(
                    logic_family="fol",
                    surface_form=node.render(),
                    ast=node,
                    confidence=max(0.3, _score_fol(text) - 0.22),
                    notes=notes,
                )
            )
    return candidates


def _parse_propositional_clause(text: str, context: ParseContext) -> LogicalNode | None:
    lower = text.lower()

    iff_match = re.match(r"^(?:se e somente se|if and only if)\s+(.+?),\s*(.+)$", lower)
    if iff_match:
        left = _atomize(iff_match.group(1), context)
        right = _atomize(iff_match.group(2), context)
        return binary("iff", left, right)

    if lower.startswith("se ") and "," in text:
        antecedent, consequent = text.split(",", 1)
        antecedent = re.sub(r"^(se|if)\s+", "", antecedent.strip(), flags=re.IGNORECASE)
        consequent = re.sub(r"^(entao|então|then)\s+", "", consequent.strip(), flags=re.IGNORECASE)
        return binary("implies", _atomize(antecedent, context), _atomize(consequent, context))

    if " somente se " in lower or " only if " in lower:
        parts = re.split(r"\b(?:somente se|only if)\b", text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            left, right = parts
            return binary("implies", _atomize(left.strip(), context), _atomize(right.strip(), context))

    if " ou " in lower:
        parts = re.split(r"\bou\b|\bor\b", text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            return binary("or", _atomize(parts[0], context), _atomize(parts[1], context))

    if " e " in lower or " and " in lower:
        parts = re.split(r"\be\b|\band\b", text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            return binary("and", _atomize(parts[0], context), _atomize(parts[1], context))

    if lower.startswith(("nao ", "não ", "not ")):
        body = re.sub(r"^(nao|não|not)\s+", "", text.strip(), flags=re.IGNORECASE)
        return negate(_atomize(body, context))

    return _atomize(text, context)


def _make_exclusive_or(node: LogicalNode) -> LogicalNode | None:
    if node.type != "or" or node.left is None or node.right is None:
        return None
    both = binary("and", node.left, node.right)
    return binary("and", node, negate(both))


def _atomize(text: str, context: ParseContext) -> LogicalNode:
    cleaned = _normalize_phrase(text)
    existing = context.symbol_map.get(cleaned)
    if existing is None:
        symbol = _make_symbol(cleaned, len(context.symbol_map))
        context.symbol_map[cleaned] = symbol
    else:
        symbol = existing
    return atom(symbol)


def _parse_fol_clause(text: str) -> tuple[LogicalNode | None, list[str]]:
    notes: list[str] = []
    clean = _clean_text(text)
    lowered = clean.lower()

    if match := re.match(r"^(todo|toda|cada|every|all)\s+([A-Za-zÀ-ÿ_]+)\s+([A-Za-zÀ-ÿ_]+)$", clean, flags=re.IGNORECASE):
        noun = _pred_name(match.group(2))
        verb = _pred_name(match.group(3))
        notes.append("Leitura universal simples do tipo 'Todo A B'.")
        return quantify("forall", "x", binary("implies", predicate(noun, "x"), predicate(verb, "x"))), notes

    if match := re.match(r"^(nenhum|nenhuma|no)\s+([A-Za-zÀ-ÿ_]+)\s+([A-Za-zÀ-ÿ_]+)$", clean, flags=re.IGNORECASE):
        noun = _pred_name(match.group(2))
        verb = _pred_name(match.group(3))
        notes.append("Leitura universal negativa simples do tipo 'Nenhum A B'.")
        body = binary("implies", predicate(noun, "x"), negate(predicate(verb, "x")))
        return quantify("forall", "x", body), notes

    if match := re.match(r"^(algum|alguma|existe|there exists|some)\s+([A-Za-zÀ-ÿ_]+)\s+([A-Za-zÀ-ÿ_]+)$", clean, flags=re.IGNORECASE):
        noun = _pred_name(match.group(2))
        verb = _pred_name(match.group(3))
        notes.append("Leitura existencial simples.")
        body = binary("and", predicate(noun, "x"), predicate(verb, "x"))
        return quantify("exists", "x", body), notes

    if match := re.match(r"^([A-Za-zÀ-ÿ_]+)\s+(?:e|eh|é|is)\s+([A-Za-zÀ-ÿ_]+)$", clean, flags=re.IGNORECASE):
        const = _const_name(match.group(1))
        pred = _pred_name(match.group(2))
        notes.append("Leitura de predicacao unaria simples.")
        return predicate(pred, const), notes

    if match := re.match(r"^([A-Za-zÀ-ÿ_]+)\s+nao\s+([A-Za-zÀ-ÿ_]+)$", lowered, flags=re.IGNORECASE):
        const = _const_name(match.group(1))
        pred = _pred_name(match.group(2))
        notes.append("Leitura de predicacao negada simples.")
        return negate(predicate(pred, const)), notes

    if "se " in lowered and "," in clean:
        antecedent_text, consequent_text = clean.split(",", 1)
        antecedent_text = re.sub(r"^(se|if)\s+", "", antecedent_text, flags=re.IGNORECASE)
        antecedent, _ = _parse_fol_clause(antecedent_text)
        consequent, _ = _parse_fol_clause(re.sub(r"^(entao|então|then)\s+", "", consequent_text, flags=re.IGNORECASE))
        if antecedent and consequent:
            notes.append("Leitura condicional em FOL restrita.")
            return binary("implies", antecedent, consequent), notes

    if " ou " in lowered:
        left_text, right_text = re.split(r"\bou\b", clean, maxsplit=1, flags=re.IGNORECASE)
        left, _ = _parse_fol_clause(left_text.strip())
        right, _ = _parse_fol_clause(right_text.strip())
        if left and right:
            notes.append("Disjuncao entre formulas FOL simples.")
            return binary("or", left, right), notes

    return None, notes


def _build_fol_alternative(text: str) -> tuple[LogicalNode, list[str]] | None:
    clean = _clean_text(text)
    if match := re.match(r"^(todo|toda|cada|every|all)\s+([A-Za-zÀ-ÿ_]+)\s+leu\s+(um|uma|a)\s+([A-Za-zÀ-ÿ_]+)$", clean, flags=re.IGNORECASE):
        noun = _pred_name(match.group(2))
        obj = _pred_name(match.group(4))
        body = binary(
            "implies",
            predicate(noun, "x"),
            quantify("exists", "y", binary("and", predicate(obj, "y"), predicate("Leu", "x", "y"))),
        )
        return quantify("forall", "x", body), ["Leitura em que cada individuo pode ter lido possivelmente um objeto diferente."]
    return None


def _pred_name(token: str) -> str:
    normalized = re.sub(r"[^A-Za-zÀ-ÿ0-9_]", "", token)
    return normalized[:1].upper() + normalized[1:].lower()


def _const_name(token: str) -> str:
    normalized = re.sub(r"[^A-Za-zÀ-ÿ0-9_]", "", token)
    return normalized[:1].lower() + normalized[1:]


def _clean_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split()).strip(" .")


def _normalize_phrase(text: str) -> str:
    lowered = _clean_text(text).lower()
    lowered = re.sub(r"^(a|o|os|as|the)\s+", "", lowered)
    return lowered


def _make_symbol(cleaned: str, index: int) -> str:
    letters = re.findall(r"[A-Za-zÀ-ÿ]+", cleaned)
    if not letters:
        return f"P{index + 1}"
    initials = "".join(part[0] for part in letters[:3]).upper()
    return initials or f"P{index + 1}"


def _build_notes(context: ParseContext) -> list[str]:
    notes = list(context.notes)
    if context.symbol_map:
        mapping = ", ".join(f"{symbol}={phrase}" for phrase, symbol in context.symbol_map.items())
        notes.append(f"Mapeamento proposicional: {mapping}.")
    return notes


def _score_propositional(text: str) -> float:
    lower = text.lower()
    if any(token in lower for token in ["se ", " if ", " ou ", " e ", " nao ", "não ", "not "]):
        return 0.9
    return 0.72


def _score_fol(text: str) -> float:
    lower = text.lower()
    if any(token in lower for token in ["todo", "cada", "nenhum", "algum", "existe"]):
        return 0.93
    return 0.76


def _merge_unique(values) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered
