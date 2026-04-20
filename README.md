# neo-mcp-logic-analyze

Language: English | [Português](README.pt-BR.md)

Python MCP server for controlled logic analysis from natural language, with an emphasis on auditable output and teaching-oriented explanations.

## What it does

This server accepts short natural-language statements and arguments, then provides structured logic-oriented outputs such as:

- controlled formalization into propositional logic;
- controlled formalization into a restricted fragment of first-order logic;
- ambiguity detection relevant to formalization;
- consistency checking;
- entailment checking;
- simple counterexamples when entailment fails;
- natural-language explanations of the formalization process.

## MCP tools

The server exposes the following MCP tools:

- `nl_parse_logic`
- `detect_ambiguities`
- `check_consistency`
- `check_entailment`
- `find_counterexample`
- `explain_formalization`
- `normalize_argument`

## MCP resources

The server also exposes these resources:

- `logic://schemas/ast-v1`
- `logic://examples/propositional`
- `logic://examples/fol`
- `logic://guides/ambiguity-taxonomy`

## MCP prompts

Available prompts:

- `formalize_argument`
- `teach_logic_step_by_step`
- `review_formalization`

## Requirements

- Python 3.11+

## Installation

Clone the repository and install the package into your current Python environment:

```powershell
git clone https://github.com/giseldo/neo-mcp-logic-analyze
cd neo-mcp-logic-analyze
python -m pip install .
```

For development dependencies:

```powershell
python -m pip install -e .[dev]
```

## Quick run

The server is designed to be launched by an MCP client over `stdio`, such as Claude Desktop, Cursor, or another MCP-compatible host.

To verify that the package is installed correctly, run:

```powershell
neo-mcp-logic-analyze
```

Expected output:

```text
neo-mcp-logic-analyze: servidor MCP iniciado em stdio; aguardando cliente...
```

The process will remain open waiting for an MCP client connection. Stop it with `Ctrl+C`.

## MCP client configuration

After installing the project with `pip install .` or `pip install -e .`, configure your MCP client like this:

```json
{
	"mcpServers": {
		"neo-mcp-logic-analyze": {
			"command": "neo-mcp-logic-analyze"
		}
	}
}
```

## Example requests

Use the following examples from your MCP client.

### Normalize an argument

Tool: `normalize_argument`

```text
text = "Se chove, a rua molha. Chove. Logo, a rua molha."
```

Expected behavior:

- premises are separated from the conclusion;
- the conclusion is identified as `a rua molha`.

### Propositional entailment

Tool: `check_entailment`

```text
premises = ["Se chove, a rua molha.", "Chove."]
conclusion = "A rua molha."
logic_family = "propositional"
```

Expected behavior:

- entailment succeeds;
- the response includes a proof sketch.

### First-order logic formalization

Tool: `nl_parse_logic`

```text
text = "Todo aluno estuda."
logic_family = "fol"
return_alternatives = true
```

Expected behavior:

- at least one candidate formalization is returned;
- one expected surface form is `forall x. (Aluno(x) -> Estuda(x))`.

### Ambiguity detection

Tool: `detect_ambiguities`

```text
text = "Todo aluno leu um livro."
```

Expected behavior:

- the server reports at least one quantifier-scope ambiguity.

### Consistency checking

Tool: `check_consistency`

```text
premises = ["Todo professor pesquisa.", "Nenhum professor pesquisa."]
logic_family = "fol"
```

Expected behavior:

- the set is inconsistent;
- the response can include an unsat core.

### Counterexample search

Tool: `find_counterexample`

```text
premises = ["Se estudo, passo.", "Passei."]
conclusion = "Estudei."
logic_family = "propositional"
```

Expected behavior:

- the conclusion is not entailed;
- the response can include a counterexample model.

## Project structure

- `src/mcp_logic_analyzer/server.py`: MCP server entrypoint, tool registration, resources, and prompts.
- `src/mcp_logic_analyzer/models/schemas.py`: Pydantic input and output schemas.
- `src/mcp_logic_analyzer/services/formalizer.py`: controlled formalization from natural language.
- `src/mcp_logic_analyzer/services/entailment.py`: entailment checking and counterexamples.
- `src/mcp_logic_analyzer/services/consistency.py`: consistency checking.
- `src/mcp_logic_analyzer/services/ambiguity.py`: ambiguity detection.
- `src/mcp_logic_analyzer/services/explainer.py`: natural-language explanations.
- `src/mcp_logic_analyzer/services/nl_normalizer.py`: argument normalization.

## Limitations

- Natural-language interpretation is heuristic and intentionally restricted.
- The project is optimized for short inputs, not long free-form texts.
- When the input is ambiguous, the server prefers warnings and alternative readings instead of forcing a single interpretation.

## Uninstall

If you installed the package with `pip install .` or `pip install -e .`, remove it with:

```powershell
pip uninstall neo-mcp-logic-analyze
```

## License

MIT
