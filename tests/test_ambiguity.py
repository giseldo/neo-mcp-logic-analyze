from mcp_logic_analyzer.services.ambiguity import detect_ambiguities


def test_detects_quantifier_scope_ambiguity():
    result = detect_ambiguities("Todo aluno leu um livro.")
    assert any(report.kind == "quantifier_scope" for report in result.reports)


def test_detects_negation_scope_ambiguity():
    result = detect_ambiguities("Maria nao convidou Ana ou Beatriz.")
    assert any(report.kind == "negation_scope" for report in result.reports)
