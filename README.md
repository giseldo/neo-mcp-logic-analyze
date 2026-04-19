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

## Documentação

A documentação foi reorganizada em Quarto, com múltiplas páginas:

- [Início](/C:/Projetos/parser_logic_mcp/docs/index.qmd)
- [Instalação](/C:/Projetos/parser_logic_mcp/docs/instalacao.qmd)
- [Uso](/C:/Projetos/parser_logic_mcp/docs/uso.qmd)
- [Referência](/C:/Projetos/parser_logic_mcp/docs/referencia.qmd)
- [Solução de problemas](/C:/Projetos/parser_logic_mcp/docs/troubleshooting.qmd)

Se você tiver o Quarto instalado:

```powershell
cd C:\Projetos\parser_logic_mcp\docs
quarto render
```

## Execução rápida

```powershell
cd C:\Projetos\parser_logic_mcp
python -m pip install -e .
$env:PYTHONPATH = "C:\Projetos\parser_logic_mcp\src"
python -m mcp_logic_analyzer.server
```

## Estrutura principal

- [server.py](/C:/Projetos/parser_logic_mcp/src/mcp_logic_analyzer/server.py): exposição MCP de tools, resources e prompts
- [schemas.py](/C:/Projetos/parser_logic_mcp/src/mcp_logic_analyzer/models/schemas.py): contratos Pydantic
- [formalizer.py](/C:/Projetos/parser_logic_mcp/src/mcp_logic_analyzer/services/formalizer.py): formalização controlada
- [entailment.py](/C:/Projetos/parser_logic_mcp/src/mcp_logic_analyzer/services/entailment.py): consequência lógica e contraexemplos
- [consistency.py](/C:/Projetos/parser_logic_mcp/src/mcp_logic_analyzer/services/consistency.py): consistência

## Limitações da V1

- a interpretação de linguagem natural é heurística e deliberadamente restrita;
- textos longos e muito ambíguos não são o foco desta versão;
- quando o texto é ambíguo, o servidor tenta devolver alertas e alternativas em vez de assumir uma única leitura.
