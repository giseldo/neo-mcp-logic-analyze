from mcp_logic_analyzer.services.entailment import check_entailment


def test_modus_ponens():
    result = check_entailment(
        premises=["Se chove, a rua molha.", "Chove."],
        conclusion="A rua molha.",
        logic_family="propositional",
    )
    assert result.entailed is True
    assert result.proof_sketch


def test_modus_tollens():
    result = check_entailment(
        premises=["Se estudo, passo.", "Nao passei."],
        conclusion="Nao estudei.",
        logic_family="propositional",
    )
    assert result.entailed is True


def test_affirming_the_consequent_is_not_entailed():
    result = check_entailment(
        premises=["Se estudo, passo.", "Passei."],
        conclusion="Estudei.",
        logic_family="propositional",
    )
    assert result.entailed is False
    assert result.counterexample is not None


def test_fol_simple_entailment():
    result = check_entailment(
        premises=["Todo aluno estuda.", "Joao e aluno."],
        conclusion="Joao e estuda.",
        logic_family="fol",
    )
    assert result.entailed is True
