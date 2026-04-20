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

## Instalação

Para fazer o download dos binários e instalar no ambiente python local

```powershell
git clone https://github.com/giseldo/neo-mcp-logic-analyze
cd neo-mcp-logic-analyze
python -m pip install .
```

## Execução rápida

O programa não precisa iniciar, ele será iniciado pelo Harness (por exemplo: claude desktop ou cursor)

Mas para verificar se está tudo funcionando, execute o comando a seguir. Ele exibe uma mensagem curta no terminal informando que o servidor subiu e ficou aguardando um cliente MCP via `stdio`. Depois feche o terminal, ou CTRL + C para parar a aplicação. Pois o controle de quandoi será iniciado será pelo Harness.

```powershell
neo-mcp-logic-analyze
```

Saída esperada:

```text
C:\neo-mcp-logic-analyze>neo-mcp-logic-analyze
neo-mcp-logic-analyze: servidor MCP iniciado em stdio; aguardando cliente...
```

## Como desinstalar

Se você instalou este app com `pip install -e .` ou `pip install .`, remova com:

```powershell
pip uninstall neo-mcp-logic-analyze
```

## Configuração do MCP no claude code ou no cursor

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

## Exemplos de teste

Use um destes exemplos no seu harness (exemplo: claude desktop ou cursor)

### Consequência lógica proposicional

```text
Use a tool check_entailment com:
premises = ["Se chove, a rua molha.", "Chove."]
conclusion = "A rua molha."
logic_family = "propositional"
```

### Formalização em FOL

```text
Use a tool nl_parse_logic com:
text = "Todo aluno estuda."
logic_family = "fol"
return_alternatives = true
```

### Ambiguidade

```text
Use a tool detect_ambiguities no texto:
"Todo aluno leu um livro."
```

### Inconsistência

```text
Use a tool check_consistency com:
premises = ["Todo professor pesquisa.", "Nenhum professor pesquisa."]
logic_family = "fol"
```

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

## Exemplo no claude desktop

Se tudo estiver correto no claude desktop quando o LLM quiser o Harness irá chamar a Tool/MCP (neo-mcp-logic-analyze). 

### Configuração

Depois de baixado (git clone) e instalado (pip install .) basta configurar no Harness o MCP Client.

```xml
{
"mcpServers": {
    "neo-mcp-logic-analyze": {
      "command": "neo-mcp-logic-analyze"
    }
  },
}
```

No claude desktop

![alt text](image-4.png)

![alt text](image-3.png)

Depois de alterar o arquivo reinicie o claude desktop.

![alt text](image-2.png)

### Exemplo de uso

![alt text](image.png)

Depois ele trará a resposta se for dada a permissão

![alt text](image-1.png)
