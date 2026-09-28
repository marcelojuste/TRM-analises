# 📋 TRM Análises — Auditoria Fiscal

Ferramenta modular de **alta performance e baixo consumo de memória** para extração, consolidação e auditoria cruzada de documentos fiscais eletrônicos (**NF-e, NFC-e e arquivos SPED Fiscal / EFD Contribuições**), com interface gráfica nativa em **CustomTkinter** e exportação de relatórios analíticos formatados em **Excel**.

O projeto foi projetado para processar grandes volumes de dados fiscais em ambientes com recursos computacionais limitados (incluindo máquinas com **Windows 7 64-bit e apenas 4 GB de RAM**).

---

## 💡 Princípios de Arquitetura & Desempenho

* **Processamento Out-of-Core & Streaming:** Leitura progressiva de arquivos XML via `xml.etree.ElementTree.iterparse`, evitando carregar arquivos inteiros em memória.
* **Execução Paralela:** Leitura paralela de lotes de arquivos XML através de `concurrent.futures.ProcessPoolExecutor`.
* **Motor Analítico OLAP descartável:** Persistência analítica ultra-rápida via **DuckDB**, configurado com limite de memória de **1 GB** e tempo de vida descartável (*Disposable Database* com limpeza de arquivos temporários ao encerrar).
* **Precisão Financeira:** Todos os valores monetários são processados e armazenados em **centavos como números inteiros (`BIGINT`/`int`)**, eliminando erros de arredondamento de Ponto Flutuante (`float`).
* **Estruturas Otimizadas:** Uso estrito de `@dataclass(slots=True, frozen=True)` para minimizar a pegada de memória do interpretador Python.
* **Interface Gráfica Leve (GUI):** Interface moderna desenvolvida em `CustomTkinter` com visualização de métricas e prévia em tabela nativa (`ttk.Treeview`).

---

## 🏗️ Estrutura do Projeto

```text
TRM-analises/
│
├── src/
│   ├── config/              # Padrões e variáveis globais da aplicação
│   ├── domain/              # Modelos de dados imutáveis (dataclasses com slots)
│   │   └── fiscal_document.py
│   ├── database/            # Conexão, lifecycle e scripts SQL do DuckDB
│   │   ├── database.py      # Context manager DisposableAuditDatabase
│   │   └── queries/         # DDL (schema.sql) e queries analíticas (audit.sql)
│   ├── repository/          # Encapsulamento de queries SQL e rotinas em lote
│   │   └── fiscal_repository.py
│   ├── parsers/             # Parsers streaming para XML e SPED
│   │   ├── xml_parser.py
│   │   └── sped_parser.py
│   ├── services/            # Orquestração do pipeline de auditoria e exportação
│   │   ├── audit_service.py
│   │   └── excel_exporter.py
│   ├── ui/                  # Componentes visuais CustomTkinter
│   │   ├── app.py           # Janela principal
│   │   ├── components/      # Cards, tabela e cabeçalhos
│   │   └── theme/           # Cores e estilos visuais
│   ├── app_paths.py         # Mapeamento e resolução de caminhos (AppPaths)
│   └── main.py              # Ponto de entrada do executável/aplicação
│
├── tests/                   # Suíte de testes unitários automatizados (pytest)
├── pyproject.toml           # Configurações do projeto e dependências
├── requirements.txt         # Lista de dependências Python
├── GEMINI.md                # Diretrizes operacionais e regras do projeto
└── README.md                # Documentação técnica do sistema
```

---

## ⚡ Fluxo de Auditoria e Processamento

```text
┌─────────────────────────┐
│ NF-e / NFC-e / SPED     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Parsers (Streaming XML) │
│  + ProcessPoolExecutor  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ FiscalDocument          │
│ (dataclass, centavos)   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ FiscalRepository        │
│ (Buffer + executemany)  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ DuckDB (Disposable)     │
│ (Audit Query / OLAP)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Exportação Excel        │
│ + Prévia na GUI         │
└────────────┬────────────┘
```

---

## 🖥️ Requisitos do Sistema

* **Sistema Operacional:** Windows 7 SP1 (64-bit) ou superior / Linux / macOS.
* **Python:** 3.10 ou superior.
* **Memória RAM:** Mínimo de 4 GB (Uso da aplicação mantido em **< 1 GB**).

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd TRM-analises
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv

# Windows (Command Prompt / PowerShell)
.\venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
python src/main.py
```

---

## 🧪 Suíte de Testes Automatizados

O projeto utiliza `pytest` para garantir a integridade dos parsers, repositórios e serviços de exportação:

```bash
# Executar todos os testes
pytest

# Executar testes com saída detalhada
pytest -v
```

---

## 📜 Licença

Propriedade privada de **TRM Sistemas**. Todos os direitos reservados.