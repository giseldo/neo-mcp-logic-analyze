# neo-mcp-logic-analyze

Idioma: Português | [English](README.md)

Servidor MCP em Python para análise lógica controlada a partir de linguagem natural, com foco em saídas auditáveis e explicações didáticas.

## O que faz

Este servidor recebe enunciados e argumentos curtos em linguagem natural e produz saídas estruturadas voltadas à lógica formal, incluindo:

- formalização controlada em lógica proposicional;
- formalização controlada em um fragmento restrito de lógica de primeira ordem;
- detecção de ambiguidades relevantes para formalização;
- verificação de consistência;
- verificação de consequência lógica;
- contraexemplos simples quando a consequência lógica falha;
- explicações em linguagem natural sobre o processo de formalização.

## Ferramentas MCP

O servidor expõe as seguintes tools MCP:

- `nl_parse_logic`
- `detect_ambiguities`
- `check_consistency`
- `check_entailment`
- `find_counterexample`
- `explain_formalization`
- `normalize_argument`

## Recursos MCP

O servidor também expõe estes resources:

- `logic://schemas/ast-v1`
- `logic://examples/propositional`
- `logic://examples/fol`
- `logic://guides/ambiguity-taxonomy`

## Prompts MCP

Prompts disponíveis:

- `formalize_argument`
- `teach_logic_step_by_step`
- `review_formalization`

## Requisitos

- Python 3.11+

## Instalação

Clone o repositório e instale o pacote no ambiente Python atual:

```powershell
git clone https://github.com/giseldo/neo-mcp-logic-analyze
cd neo-mcp-logic-analyze
python -m pip install .
```

Para dependências de desenvolvimento:

```powershell
python -m pip install -e .[dev]
```

## Execução rápida

O servidor foi feito para ser iniciado por um cliente MCP via `stdio`, como Claude Desktop, Cursor ou outro host compatível com MCP.

Para verificar se a instalação está correta, execute:

```powershell
neo-mcp-logic-analyze
```

Saída esperada:

```text
neo-mcp-logic-analyze: servidor MCP iniciado em stdio; aguardando cliente...
```

O processo permanecerá aberto aguardando a conexão de um cliente MCP. Para encerrar, use `Ctrl+C`.

## Configuração do cliente MCP

Depois de instalar o projeto com `pip install .` ou `pip install -e .`, configure o seu cliente MCP assim:

```json
{
  "mcpServers": {
    "neo-mcp-logic-analyze": {
      "command": "neo-mcp-logic-analyze"
    }
  }
}
```

## Exemplos de uso

Use os exemplos abaixo a partir do seu cliente MCP.

### Normalizar um argumento

Tool: `normalize_argument`

```text
text = "Se chove, a rua molha. Chove. Logo, a rua molha."
```

Comportamento esperado:

- as premissas são separadas da conclusão;
- a conclusão é identificada como `a rua molha`.

### Consequência lógica proposicional

Tool: `check_entailment`

```text
premises = ["Se chove, a rua molha.", "Chove."]
conclusion = "A rua molha."
logic_family = "propositional"
```

Comportamento esperado:

- a consequência lógica é válida;
- a resposta inclui um esboço de prova.

### Formalização em lógica de primeira ordem

Tool: `nl_parse_logic`

```text
text = "Todo aluno estuda."
logic_family = "fol"
return_alternatives = true
```

Comportamento esperado:

- pelo menos uma formalização candidata é retornada;
- uma surface form esperada é `forall x. (Aluno(x) -> Estuda(x))`.

### Detecção de ambiguidade

Tool: `detect_ambiguities`

```text
text = "Todo aluno leu um livro."
```

Comportamento esperado:

- o servidor reporta pelo menos uma ambiguidade de escopo de quantificador.

### Verificação de consistência

Tool: `check_consistency`

```text
premises = ["Todo professor pesquisa.", "Nenhum professor pesquisa."]
logic_family = "fol"
```

Comportamento esperado:

- o conjunto é inconsistente;
- a resposta pode incluir um núcleo insatisfatível.

### Busca de contraexemplo

Tool: `find_counterexample`

```text
premises = ["Se estudo, passo.", "Passei."]
conclusion = "Estudei."
logic_family = "propositional"
```

Comportamento esperado:

- a conclusão não decorre das premissas;
- a resposta pode incluir um modelo de contraexemplo.

## Estrutura do projeto

- `src/mcp_logic_analyzer/server.py`: ponto de entrada do servidor MCP, registro de tools, resources e prompts.
- `src/mcp_logic_analyzer/models/schemas.py`: schemas de entrada e saída com Pydantic.
- `src/mcp_logic_analyzer/services/formalizer.py`: formalização controlada a partir da linguagem natural.
- `src/mcp_logic_analyzer/services/entailment.py`: verificação de consequência lógica e contraexemplos.
- `src/mcp_logic_analyzer/services/consistency.py`: verificação de consistência.
- `src/mcp_logic_analyzer/services/ambiguity.py`: detecção de ambiguidades.
- `src/mcp_logic_analyzer/services/explainer.py`: explicações em linguagem natural.
- `src/mcp_logic_analyzer/services/nl_normalizer.py`: normalização de argumentos.

## Limitações

- A interpretação da linguagem natural é heurística e intencionalmente restrita.
- O projeto é otimizado para entradas curtas, não para textos longos e livres.
- Quando a entrada é ambígua, o servidor prefere retornar alertas e leituras alternativas em vez de forçar uma única interpretação.

## Desinstalação

Se você instalou o pacote com `pip install .` ou `pip install -e .`, remova com:

```powershell
pip uninstall neo-mcp-logic-analyze
```

## Licença

MIT