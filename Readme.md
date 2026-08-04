# 🔍 Sistema Desktop de Auditoria Fiscal

> Ferramenta corporativa desktop para validação, auditoria e cruzamento de arquivos fiscais (XMLs de NF-e/NFC-e vs. Escrituração SPED Fiscal - Bloco C).

---

## 📌 1. Visão Geral e Arquitetura

O sistema adota uma **Arquitetura Monolítica em Camadas (*Layered Monolith*)**, focada em baixa complexidade, alta manutenibilidade, execução 100% local e distribuição como executável único (`.exe`) sem dependência de servidores ou bancos externos.

```
src/
├── presentation/   # Interface gráfica com CustomTkinter
├── services/       # Regras de negócio, orquestração e fluxos de auditoria
├── parsers/        # Leitura nativa de XMLs (xml.etree) e SPED TXT (open)
├── database/       # Conexão, esquemas e consultas SQL puras no DuckDB
└── loggers/        # Gravação e estrutura dos relatórios de divergência em JSON via TinyDB
```

---

## 🛠️ 2. Tech Stack

* **Linguagem & Ingestão:** Python 3.11+ utilizando bibliotecas nativas (`xml.etree.ElementTree` e `open()`).
* **Engine de Dados:** [DuckDB](https://duckdb.org/) (Banco de dados OLAP analítico embarcado executando SQL puro).
* **Logs & Resultados:** [TinyDB](https://tinydb.readthedocs.io/) (Engine NoSQL para gravação de documentos JSON de divergências).
* **Interface Gráfica (GUI):** [CustomTkinter](https://customtkinter.tsets.in/) (Visual moderno com suporte a Dark Mode).
* **Empacotamento:** [PyInstaller](https://pyinstaller.org/) (Geração do executável portátil `.exe`).

---

## 🚀 3. Como Configurar o Ambiente de Desenvolvimento

### Pré-requisitos
* Python 3.11 ou superior instalado.

### Passo 1: Clonar o repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### Passo 2: Criar e ativar o ambiente virtual (Recomendado)
* **Windows (PowerShell/CMD):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```

### Passo 3: Instalar as dependências
```bash
python -m pip install -r requirements.txt
```

---

## 📋 4. Principais Comandos

### Executar a aplicação em ambiente de desenvolvimento
```bash
python src/main.py
```

### Gerar/Atualizar o arquivo `requirements.txt`
```bash
python -m pip freeze > requirements.txt
```

### Gerar o Executável (.exe) para Produção
```bash
pyinstaller --noconfirm --onedir --windowed --name "AuditoriaFiscal" src/main.py
```

---

## 📅 5. Roadmap de Desenvolvimento (16 Semanas)

- [ ] **Fase 1 (S1–S4):** Configuração do repositório, ambiente virtual, conexão com DuckDB e criação do schema SQL.
- [ ] **Fase 2 (S5–S8):** Desenvolvimento dos parsers nativos de XML e SPED TXT com rotinas de *bulk insert*.
- [ ] **Fase 3 (S9–S12):** Escrita das queries SQL de cruzamento (Notas Omissas/Divergências) e orquestrador de logs em TinyDB.
- [ ] **Fase 4 (S13–S16):** Criação da interface em CustomTkinter, testes de integração e geração do `.exe` via PyInstaller.

---

## 📊 6. Formato dos Logs de Divergência

Os relatórios gerados ficam armazenados em arquivos `.json` legíveis gerados via TinyDB, contendo o resumo da execução e a lista detalhada de divergências encontradas entre as notas e a escrituração fiscal.