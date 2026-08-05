# Diretrizes de Desenvolvimento - Sistema de Auditoria Fiscal

Este arquivo serve como guia rápido de comandos, estilo de código e arquitetura para o desenvolvimento da aplicação.

## 🛠️ Comandos Principais

### Ambiente e Dependências
* Ativar ambiente virtual (Windows): `.venv\Scripts\activate`
* Instalar dependências: `python -m pip install -r requirements.txt`
* Atualizar dependências: `python -m pip freeze > requirements.txt`

### Execução e Testes
* Executar aplicação: `python src/main.py`
* Executar testes: `pytest`
* Executar teste específico: `pytest tests/test_nome.py`

### Compilação (Build)
* Gerar executável de produção: `pyinstaller --noconfirm --onedir --windowed --name "AuditoriaFiscal" src/main.py`

---

## 🎨 Diretrizes de Estilo e Código

### Idioma de Comunicação e Código
* **Todas as respostas, explicações e documentações devem ser em Português (Brasil).**
* O código em si (nomes de variáveis, funções, classes, logs internos) deve ser escrito em inglês para manter o padrão técnico da linguagem.
* Comentários explicativos no código podem ser escritos em português.

### Arquitetura de Software (Layered Monolith)
Respeitar rigorosamente a divisão em camadas sob a pasta `src/`:
1. `presentation/`: Interfaces gráficas usando `customtkinter`.
2. `services/`: Regras de negócio, cálculos, cruzamentos e orquestração.
3. `parsers/`: Ingestão nativa de dados brutos (`xml.etree.ElementTree` para XML e `open` nativo para SPED TXT).
4. `database/`: Conexão, tabelas e scripts SQL puros no `DuckDB`.
5. `loggers/`: Formatação e gravação de logs de divergência em JSON via `TinyDB`.

### Regras de Implementação Estritas (Tech Stack)
* **Sem Pandas ou Polars:** Processar volumes de dados usando o DuckDB para consultas analíticas pesadas (SQL puro) ou iteradores nativos do Python em memória para arquivos individuais.
* **Sem ORM (SQLAlchemy, etc.):** Todas as operações no DuckDB devem ser executadas com SQL bruto e parametrização de consultas para segurança e desempenho.
* **Tipagem Estática:** Utilizar as anotações de tipo do Python (`typing`) em todas as novas funções e métodos para garantir manutenibilidade.
* **Testabilidade:** Sempre acompanhar novos desenvolvimentos ou correções de bugs com testes correspondentes utilizando `pytest`.
