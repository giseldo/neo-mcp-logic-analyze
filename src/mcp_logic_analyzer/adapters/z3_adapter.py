from __future__ import annotations

from itertools import combinations, product

from mcp_logic_analyzer.models.ast import LogicalNode

try:
    import z3  # type: ignore
except ImportError:  # pragma: no cover
    z3 = None


def z3_available() -> bool:
    return z3 is not None


def finite_model_search(nodes: list[LogicalNode], constants: set[str] | None = None, max_domain_size: int = 3) -> dict | None:
    universe = sorted(constants or _collect_constants(nodes))
    if not universe:
        universe = ["d0"]
    predicates = _collect_predicates(nodes)
    for extra_size in range(len(universe), max(len(universe), max_domain_size) + 1):
        domain = list(universe)
        while len(domain) < extra_size:
            domain.append(f"d{len(domain)}")
        model = _enumerate_models(nodes, domain, predicates)
        if model is not None:
            return model
    return None


def finite_countermodel(premises: list[LogicalNode], conclusion: LogicalNode, constants: set[str] | None = None, max_domain_size: int = 3) -> dict | None:
    universe = sorted(constants or _collect_constants(premises + [conclusion]))
    if not universe:
        universe = ["d0"]
    predicates = _collect_predicates(premises + [conclusion])
    for extra_size in range(len(universe), max(len(universe), max_domain_size) + 1):
        domain = list(universe)
        while len(domain) < extra_size:
            domain.append(f"d{len(domain)}")
        for interpretation in _iter_interpretations(predicates, domain):
            if all(_eval_fol(node, interpretation, {}, domain) for node in premises) and not _eval_fol(conclusion, interpretation, {}, domain):
                return _serialize_model(domain, interpretation)
    return None


def minimal_unsat_core(nodes: list[LogicalNode]) -> list[int]:
    if finite_model_search(nodes) is not None:
        return []
    indexes = list(range(len(nodes)))
    for size in range(1, len(nodes) + 1):
        for subset in combinations(indexes, size):
            formulas = [nodes[i] for i in subset]
            if finite_model_search(formulas) is None:
                return list(subset)
    return indexes


def _enumerate_models(nodes: list[LogicalNode], domain: list[str], predicates: dict[str, int]) -> dict | None:
    for interpretation in _iter_interpretations(predicates, domain):
        if all(_eval_fol(node, interpretation, {}, domain) for node in nodes):
            return _serialize_model(domain, interpretation)
    return None


def _iter_interpretations(predicates: dict[str, int], domain: list[str]):
    predicate_items = list(predicates.items())
    tuple_spaces = {
        name: list(product(domain, repeat=arity))
        for name, arity in predicate_items
    }
    choice_spaces = [
        list(product([False, True], repeat=len(tuple_spaces[name])))
        for name, _arity in predicate_items
    ]
    for choices in product(*choice_spaces) if choice_spaces else [()]:
        interpretation: dict[str, set[tuple[str, ...]]] = {}
        for idx, (name, _arity) in enumerate(predicate_items):
            tuples = tuple_spaces[name]
            if not tuples:
                interpretation[name] = set()
                continue
            mask = choices[idx]
            interpretation[name] = {tuples[position] for position, truth in enumerate(mask) if truth}
        yield interpretation


def _eval_fol(node: LogicalNode, interpretation: dict[str, set[tuple[str, ...]]], env: dict[str, str], domain: list[str]) -> bool:
    if node.type == "predicate":
        args = tuple(env.get(arg, arg) for arg in node.args)
        return args in interpretation.get(node.name or "Pred", set())
    if node.type == "not" and node.body:
        return not _eval_fol(node.body, interpretation, env, domain)
    if node.type == "and" and node.left and node.right:
        return _eval_fol(node.left, interpretation, env, domain) and _eval_fol(node.right, interpretation, env, domain)
    if node.type == "or" and node.left and node.right:
        return _eval_fol(node.left, interpretation, env, domain) or _eval_fol(node.right, interpretation, env, domain)
    if node.type == "implies" and node.left and node.right:
        return (not _eval_fol(node.left, interpretation, env, domain)) or _eval_fol(node.right, interpretation, env, domain)
    if node.type == "iff" and node.left and node.right:
        return _eval_fol(node.left, interpretation, env, domain) == _eval_fol(node.right, interpretation, env, domain)
    if node.type == "forall" and node.var and node.body:
        return all(_eval_fol(node.body, interpretation, {**env, node.var: value}, domain) for value in domain)
    if node.type == "exists" and node.var and node.body:
        return any(_eval_fol(node.body, interpretation, {**env, node.var: value}, domain) for value in domain)
    raise ValueError(f"Unsupported FOL node: {node.type}")


def _collect_constants(nodes: list[LogicalNode]) -> set[str]:
    found: set[str] = set()
    for node in nodes:
        found.update(_collect_constants_from_node(node))
    return found


def _collect_constants_from_node(node: LogicalNode) -> set[str]:
    if node.type == "predicate":
        return {arg for arg in node.args if arg and arg[0].islower()}
    found: set[str] = set()
    if node.body:
        found.update(_collect_constants_from_node(node.body))
    if node.left:
        found.update(_collect_constants_from_node(node.left))
    if node.right:
        found.update(_collect_constants_from_node(node.right))
    if node.var and node.var in found:
        found.remove(node.var)
    return found


def _collect_predicates(nodes: list[LogicalNode]) -> dict[str, int]:
    predicates: dict[str, int] = {}
    for node in nodes:
        _collect_predicates_from_node(node, predicates)
    return predicates


def _collect_predicates_from_node(node: LogicalNode, predicates: dict[str, int]) -> None:
    if node.type == "predicate":
        predicates[node.name or "Pred"] = len(node.args)
        return
    if node.body:
        _collect_predicates_from_node(node.body, predicates)
    if node.left:
        _collect_predicates_from_node(node.left, predicates)
    if node.right:
        _collect_predicates_from_node(node.right, predicates)


def _serialize_model(domain: list[str], interpretation: dict[str, set[tuple[str, ...]]]) -> dict:
    return {
        "domain": domain,
        "predicates": {
            name: sorted([list(entry) for entry in tuples])
            for name, tuples in interpretation.items()
        },
    }
