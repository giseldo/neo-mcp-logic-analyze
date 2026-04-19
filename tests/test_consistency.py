from mcp_logic_analyzer.services.consistency import check_consistency


def test_propositional_consistency():
    result = check_consistency(["Chove.", "Nao venta."], "propositional")
    assert result.consistent is True


def test_fol_inconsistency():
    result = check_consistency(["Todo professor pesquisa.", "Nenhum professor pesquisa."], "fol")
    assert result.consistent is False
    assert result.unsat_core == [0, 1]
