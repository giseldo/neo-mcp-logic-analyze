from __future__ import annotations

import re

from mcp_logic_analyzer.models.schemas import NormalizeArgumentOutput


CONCLUSION_MARKERS = [
    "logo",
    "therefore",
    "thus",
    "portanto",
    "entao",
    "então",
    "hence",
]


def normalize_argument(text: str) -> NormalizeArgumentOutput:
    cleaned = _normalize_spacing(text)
    segments = _split_sentences(cleaned)
    premises: list[str] = []
    conclusion: str | None = None

    for segment in segments:
        lower = segment.lower()
        matched_marker = next((marker for marker in CONCLUSION_MARKERS if re.search(rf"\b{re.escape(marker)}\b", lower)), None)
        if matched_marker:
            before, after = re.split(rf"\b{re.escape(matched_marker)}\b", segment, maxsplit=1, flags=re.IGNORECASE)
            before = before.strip(" ,;:")
            after = after.strip(" ,;:.")
            if before:
                premises.append(before)
            if after:
                conclusion = after
            continue
        premises.append(segment.strip(" ."))

    if conclusion is None and len(premises) > 1:
        conclusion = premises.pop()

    assumptions: list[str] = []
    if conclusion is None and premises:
        assumptions.append("Nenhum marcador explicito de conclusao foi encontrado; o texto foi tratado como uma unica premissa.")

    explanation = "Argumento normalizado em premissas e conclusao." if conclusion else "Texto tratado como conjunto de premissas."
    return NormalizeArgumentOutput(
        status="ok",
        premises=[item for item in premises if item],
        conclusion=conclusion,
        implicit_assumptions=assumptions,
        explanation=explanation,
    )


def _normalize_spacing(text: str) -> str:
    collapsed = " ".join(text.replace("\n", " ").split())
    return collapsed.strip()


def _split_sentences(text: str) -> list[str]:
    if not text:
        return []
    raw = re.split(r"(?<=[.!?;])\s+", text)
    segments = [piece.strip().strip(".") for piece in raw if piece.strip()]
    return segments
