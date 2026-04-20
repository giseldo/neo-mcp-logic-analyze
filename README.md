# neo-mcp-logic-analyze

Servidor MCP em Python para analisar enunciados em linguagem natural e produzir uma formalização lógica controlada, com foco didático e auditável.

## O que este serviço faz

- formaliza textos curtos em lógica proposicional;
- formaliza um fragmento controlado de lógica de primeira ordem;
- detecta ambiguidades relevantes para formalização;
- verifica consistência e consequência lógica;
- produz contraexemplos simples e explicações em linguagem natural.

## Ferramentas MCP expostas

- `nl_parse_logic`
- `detect_ambiguities`
- `check_consistency`
- `check_entailment`
- `find_counterexample`
- `explain_formalization`
- `normalize_argument`

## Execução rápida

```powershell
cd .
python -m pip install -e .
$env:PYTHONPATH = "$PWD\src"
python -m mcp_logic_analyzer.server
```

## Configuração do MCP

Exemplo de configuração para clientes MCP (chave `mcpServers`), após instalar o projeto com `pip install -e .`:

```json
{
	"mcpServers": {
		"neo-mcp-logic-analyze": {
			"command": "neo-mcp-logic-analyze"
		}
	}
}
```

Alternativa para rodar direto do diretório atual do projeto (sem usar o script instalado):

```json
{
	"mcpServers": {
		"neo-mcp-logic-analyze": {
			"command": "python",
			"args": ["-m", "mcp_logic_analyzer.server"],
			"cwd": ".",
			"env": {
				"PYTHONPATH": "src"
			}
		}
	}
}
```

Se o seu cliente MCP não aceitar `cwd` relativo, informe o caminho absoluto da pasta do projeto no campo `cwd`.

## Estrutura principal

- [server.py](src/mcp_logic_analyzer/server.py): exposição MCP de tools, resources e prompts
- [schemas.py](src/mcp_logic_analyzer/models/schemas.py): contratos Pydantic
- [formalizer.py](src/mcp_logic_analyzer/services/formalizer.py): formalização controlada
- [entailment.py](src/mcp_logic_analyzer/services/entailment.py): consequência lógica e contraexemplos
- [consistency.py](src/mcp_logic_analyzer/services/consistency.py): consistência

## Limitações da V1

- a interpretação de linguagem natural é heurística e deliberadamente restrita;
- textos longos e muito ambíguos não são o foco desta versão;
- quando o texto é ambíguo, o servidor tenta devolver alertas e alternativas em vez de assumir uma única leitura.


