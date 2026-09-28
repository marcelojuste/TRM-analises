# 📋 TRM Análises — Auditoria Fiscal

Ferramenta modular de **alta performance e baixo consumo de memória** para extração, consolidação e auditoria cruzada de documentos fiscais eletrônicos (**NF-e, NFC-e e arquivos SPED Fiscal / EFD Contribuições**), com interface gráfica nativa em **CustomTkinter** e exportação de relatórios analíticos formatados em **Excel**.

O projeto foi projetado para processar grandes volumes de dados fiscais em ambientes com recursos computacionais limitados (incluindo máquinas com **Windows 7 64-bit e apenas 4 GB de RAM**).

---

## 💡 Princípios de Arquitetura & Desempenho

* **Processamento Out-of-Core & Streaming:** Leitura progressiva de arquivos XML via `xml.etree.ElementTree.iterparse`, evitando carregar arquivos inteiros em memória.
* **Execução Paralela:** Leitura paralela de lotes de arquivos XML através de `concurrent.futures.ProcessPoolExecutor`.
* **Motor Analítico OLAP Descartável:** Persistência analítica ultra-rápida via **DuckDB**, configurado com limite de memória de **1 GB** e tempo de vida descartável (*Disposable Database* com limpeza de arquivos na pasta `temp_files` ao encerrar).
* **Precisão Financeira:** Todos os valores monetários são processados e armazenados em **centavos como números inteiros (`BIGINT`/`int`)**, eliminando erros de arredondamento de Ponto Flutuante (`float`).
* **Estruturas Otimizadas e Leves:** Manipulação direta de tuplas e estruturas de dados enxutas sem o overhead de abstrações pesadas.
* **Interface Gráfica Leve (GUI):** Interface moderna desenvolvida em `CustomTkinter` localizada no diretório `views`, com suporte a temas, seleção de arquivos, visualização de métricas e prévia em tabela nativa (`ttk.Treeview`).

---

## 🏗️ Estrutura do Projeto

```text
TRM-analises/
│
├── .github/                 # Workflows e automações CI/CD
├── .vscode/                 # Configurações do ambiente de desenvolvimento
│
├── src/
│   ├── database/            # Gerenciamento de conexão DuckDB e scripts SQL
│   │   ├── queries/         # DDL (schema.sql) e queries analíticas (audit.sql)
│   │   └── database.py      # Context Manager (DisposableAuditDatabase)
│   │
│   ├── models/              # Modelos e definições de estruturas de documentos
│   │   ├── fiscal_document.py
│   │   └── sped_document.py
│   │
│   ├── outputs/             # Diretório de destino dos relatórios gerados (.xlsx)
│   │
│   ├── parsers/             # Parsers streaming para extração de XML e SPED
│   │   ├── sped_parser.py
│   │   └── xml_parser.py
│   │
│   ├── repositories/        # Camada de persistência e gravação em lote
│   │   └── fiscal_repository.py
│   │
│   ├── services/            # Serviços de orquestração e exportação
│   │   ├── audit_service.py
│   │   └── excel_exporter.py
│   │
│   ├── temp_files/          # Arquivos temporários e banco DuckDB descartável
│   │
│   ├── views/               # Interface Gráfica (GUI) em CustomTkinter
│   │   ├── assets/          # Ícones, imagens e recursos visuais
│   │   ├── components/      # Componentes de UI (Header, FileCard, MetricCard, ResultTable)
│   │   └── app.py           # Janela principal da aplicação
│   │
│   ├── app_paths.py         # Mapeamento e resolução de caminhos imutáveis (AppPaths)
│   └── main.py              # Ponto de entrada do sistema
│
├── tests/                   # Suíte de testes unitários automatizados (pytest)
├── .gitignore
├── conftest.py              # Configurações globais e fixtures do pytest
├── pyproject.toml           # Configurações do projeto e ferramentas de build
├── Readme.md                # Documentação técnica do sistema
└── requirements.txt         # Dependências do projeto Python
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
│ Tuplas de Dados         │
│ (Chave, CNPJ, Centavos) │
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
│ Relatório Excel         │
│ + Prévia na GUI (Views) │
└─────────────────────────┘
```

---

## 🖥️ Requisitos do Sistema

* **Sistema Operacional:** Windows 7 SP1 (64-bit) ou superior / Linux / macOS.
* **Python:** 3.10 ou superior.
* **Memória RAM:** Mínimo de 4 GB (Uso da aplicação mantido abaixo de **1 GB**).

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

O projeto utiliza `pytest` para validação e testes isolados dos parsers, repositórios e serviços de auditoria:

```bash
# Executar todos os testes
pytest

# Executar testes com saída detalhada
pytest -v
```

---

## 📜 Licença

Propriedade privada de **TRM Sistemas**. Todos os direitos reservados.