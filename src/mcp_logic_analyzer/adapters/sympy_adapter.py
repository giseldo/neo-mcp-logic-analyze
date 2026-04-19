from __future__ import annotations

from itertools import product

from sympy import And, Equivalent, Implies, Not, Or, Symbol, satisfiable

from mcp_logic_analyzer.models.ast import LogicalNode


def to_sympy(node: LogicalNode):
    if node.type == "atom":
        return Symbol(node.name or "P")
    if node.type == "not" and node.body is not None:
        return Not(to_sympy(node.body))
    if node.type == "and" and node.left is not None and node.right is not None:
        return And(to_sympy(node.left), to_sympy(node.right))
    if node.type == "or" and node.left is not None and node.right is not None:
        return Or(to_sympy(node.left), to_sympy(node.right))
    if node.type == "implies" and node.left is not None and node.right is not None:
        return Implies(to_sympy(node.left), to_sympy(node.right))
    if node.type == "iff" and node.left is not None and node.right is not None:
        return Equivalent(to_sympy(node.left), to_sympy(node.right))
    raise ValueError(f"Node type {node.type} is not supported by the propositional adapter.")


def satisfiable_model(nodes: list[LogicalNode]) -> dict[str, bool] | None:
    if not nodes:
        return {}
    expr = And(*[to_sympy(node) for node in nodes])
    result = satisfiable(expr, all_models=False)
    if result is False:
        return None
    normalized: dict[str, bool] = {}
    for key, value in result.items():
        normalized[str(key)] = bool(value)
    return normalized


def counterexample_model(premises: list[LogicalNode], conclusion: LogicalNode) -> dict[str, bool] | None:
    expr = And(*[to_sympy(node) for node in premises], Not(to_sympy(conclusion)))
    result = satisfiable(expr, all_models=False)
    if result is False:
        return None
    return {str(key): bool(value) for key, value in result.items()}


def truth_table_counterexample(premises: list[LogicalNode], conclusion: LogicalNode) -> dict[str, bool] | None:
    atoms = sorted(_collect_atoms_list(premises + [conclusion]))
    if not atoms:
        return None
    for assignment in product([False, True], repeat=len(atoms)):
        valuation = dict(zip(atoms, assignment))
        if all(_eval_propositional(node, valuation) for node in premises) and not _eval_propositional(conclusion, valuation):
            return valuation
    return None


def _collect_atoms_list(nodes: list[LogicalNode]) -> set[str]:
    found: set[str] = set()
    for node in nodes:
        found.update(_collect_atoms(node))
    return found


def _collect_atoms(node: LogicalNode) -> set[str]:
    if node.type == "atom" and node.name:
        return {node.name}
    if node.type == "not" and node.body:
        return _collect_atoms(node.body)
    if node.left or node.right:
        left = _collect_atoms(node.left) if node.left else set()
        right = _collect_atoms(node.right) if node.right else set()
        return left | right
    return set()


def _eval_propositional(node: LogicalNode, valuation: dict[str, bool]) -> bool:
    if node.type == "atom":
        return bool(valuation[node.name or "P"])
    if node.type == "not" and node.body:
        return not _eval_propositional(node.body, valuation)
    if node.type == "and" and node.left and node.right:
        return _eval_propositional(node.left, valuation) and _eval_propositional(node.right, valuation)
    if node.type == "or" and node.left and node.right:
        return _eval_propositional(node.left, valuation) or _eval_propositional(node.right, valuation)
    if node.type == "implies" and node.left and node.right:
        return (not _eval_propositional(node.left, valuation)) or _eval_propositional(node.right, valuation)
    if node.type == "iff" and node.left and node.right:
        return _eval_propositional(node.left, valuation) == _eval_propositional(node.right, valuation)
    raise ValueError(f"Unsupported propositional node: {node.type}")
