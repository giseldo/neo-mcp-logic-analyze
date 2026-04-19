from mcp_logic_analyzer.services.formalizer import parse_logic
from mcp_logic_analyzer.services.nl_normalizer import normalize_argument


def test_normalize_argument_extracts_conclusion():
    result = normalize_argument("Se chove, a rua molha. Chove. Logo, a rua molha.")
    assert result.premises == ["Se chove, a rua molha", "Chove"]
    assert result.conclusion == "a rua molha"


def test_parse_propositional_conditional():
    result = parse_logic("Se chove, a rua molha.", "propositional")
    assert result.candidates
    assert result.candidates[0].ast.type == "implies"


def test_parse_fol_universal():
    result = parse_logic("Todo aluno estuda.", "fol")
    assert result.candidates
    assert result.candidates[0].surface_form == "forall x. (Aluno(x) -> Estuda(x))"


def test_parse_fol_ambiguity_alternative():
    result = parse_logic("Todo aluno leu um livro.", "fol", return_alternatives=True)
    assert len(result.candidates) >= 1
    assert result.ambiguities
