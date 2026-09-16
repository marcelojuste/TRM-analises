# 📋 Contexto do Projeto & Diretrizes do Assistente (GEMINI.md)

Este documento define os limites operacionais, arquitetura e convenções do projeto. O assistente de IA deve seguir **estritamente** estas diretrizes em todas as respostas e edições de código.

---

## 🛠️ 1. Restrições do Ambiente de Hardware
- **Sistema Operacional Alvo:** Windows 7 SP1 (64-bit).
- **Recursos Disponíveis:** 4 GB RAM / CPU Dual-Core.
- **Diretriz de Desempenho:** 
  - Foco absoluto em baixo consumo de memória.
  - Priorizar processamento **Out-of-Core** e operações em lote.
  - Proibido carregar arquivos XML/SPED inteiros em memória de uma só vez.

---

## 🏗️ 2. Arquitetura da Aplicação
A aplicação segue uma arquitetura orientada a objetos (POO) minimalista, mantendo clara separação de responsabilidades:

1. **Domain (`src/domain`):** Modelos de dados imutáveis usando `@dataclass(slots=True, frozen=True)`.
2. **Infrastructure (`src/config`, `src/database`):** 
   - Gerenciamento de caminhos imutáveis via `pathlib.Path` com o *Singleton* de módulo (`PATHS`).
   - Gerenciamento de conexão com DuckDB descartável via *Context Manager* (`DisposableAuditDatabase`).
3. **Repository (`src/repository`):** Encapsulamento de queries SQL e execução em lote via `executemany`.

---

## 💾 3. Estratégia de Dados & Banco de Dados
- **Engine Database:** DuckDB (Arquivo descartável `.duckdb`).
- **Precisão Financeira:** TODOS os campos monetários devem ser processados e armazenados em **centavos como inteiros (`int`)**. Jamais usar `float`.
- **Chaves de Acesso:** Extrair o modelo fiscal (55/65) via `SUBSTR` da chave de acesso do documento. Não criar colunas redundantes para o modelo.
- **Limites do Banco:** Tópicos de configuração de sessão no DuckDB obrigatórios:
  - `SET memory_limit = '1GB';`
  - `SET threads = 2;`

---

## 🐍 4. Padrões de Código Python

- **Typing:** Uso estrito de *Type Hints* em todas as funções, métodos e atributos (`def func(param: Path) -> None:`).
- **Gerenciamento de Recursos:** Sempre manipular o banco dentro do bloco `with DisposableAuditDatabase(...) as conn:`.
- **Privacidade & Encapsulamento:**
  - Usar underline único (`_metodo`) para métodos/atributos de convenção privada.
  - Evitar duplo underline (`__`) a menos que *Name Mangling* seja estritamente necessário.
- **Factory Methods:** Utilizar o decorador `@classmethod` para construtores alternativos (`from_root()`, `from_sped_line()`).

---

## 🚫 5. O que a IA NÃO deve fazer (Proibições)

1. **NÃO** sugerir bibliotecas pesadas como `pandas` ou `polars` para parsing ou manipulação de dados.
2. **NÃO** alterar o tipo de dados de valores monetários para `float`.
3. **NÃO** remover a destruição e limpeza do arquivo `.duckdb` no método `__exit__`.
4. **NÃO** sugerir código com variáveis globais mutáveis fora da estrutura de classes/módulos estabelecida.