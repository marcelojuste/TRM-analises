# TRM Análises - Auditor Fiscal

O **TRM Análises - Auditor Fiscal** é uma aplicação desktop de alta performance em Python desenvolvida para auditoria, cruzamento e conciliação de documentos fiscais. O sistema realiza o confronto entre arquivos XML (NF-e/NFC-e) e livros fiscais digitais (**SPED ICMS/IPI**, **EFD Contribuições** e **Sintegra**), utilizando **DuckDB** para consultas analíticas em memória e **Pandas** para manipulação estruturada de dados.

---

## 🚀 Funcionalidades Principais

* **Processamento Multiformato:**
  * **Documentos XML:** Leitura e validação de NF-e (Modelo 55) e NFC-e (Modelo 65), com filtragem automática de ambientes de produção, validação de chave de acesso (44 dígitos) e conversão de valores para centavos (evitando erros de ponto flutuante).
  * **Arquivos SPED:** Suporte a arquivos **EFD ICMS/IPI** e **EFD Contribuições**, com identificação automática da estrutura e extração dos registros C100.
  * **Arquivos Sintegra:** Leitura de registros no formato de largura fixa (Registros 10, 50, 51 e 61) com mapeamento de CFOP e normalização de status do documento.

* **Performance & Motor de Análise:**
  * **DuckDB Integrado:** Execução de queries SQL de conciliação diretamente em memória, garantindo alta velocidade no cruzamento de dados.
  * **Processamento Concorrente:** Leitura multithreaded de arquivos XML via `ThreadPoolExecutor`.
  * **Priorização de Processo:** Ajuste automático da prioridade de execução do sistema (Win32 / OS Nice) para evitar o travamento da máquina durante auditorias volumosas.

* **Interface Gráfica Modesta e Moderna:**
  * Desenvolvida com `CustomTkinter` e suporte a *Drag & Drop* (`TkinterDnD2`).
  * Alternância dinâmica entre os modos de operação (SPED x Sintegra).
  * Visualização gráfica de métricas de totais e divergências.
  * Tabela de prévia de resultados com exportação direta para relatórios formatados em **Excel**.

---

## 📁 Estrutura do Projeto

```
TRM-analises/
├── .github/
│   └── workflows/
│       └── tests.yml            # Pipeline de Integração Contínua (CI)
├── src/
│   ├── models/                  # Modelos de dados
│   │   ├── base_model.py        # Modelo base de documentos fiscais
│   │   ├── sintegra_model.py    # Modelo de dados do Sintegra
│   │   ├── sped_model.py        # Modelo de dados do SPED
│   │   └── xml_model.py         # Modelo de dados de XMLs (NF-e/NFC-e)
│   ├── outputs/                 # Diretório padrão para relatórios exportados
│   ├── parsers/                 # Leitores e interpretadores de arquivos
│   │   ├── base_parser.py       # Leitor base com detecção de encoding (utf-8, latin-1)
│   │   ├── sintegra_parser.py   # Parser de arquivos Sintegra
│   │   ├── sped_parser.py       # Parser de arquivos SPED
│   │   └── xml_parser.py        # Parser de arquivos XML
│   ├── repositories/            # Armazenamento em memória e tratamento
│   │   ├── scripts/             # Scripts SQL de auditoria (DuckDB)
│   │   └── fiscal_repository.py # Consolidação de DataFrames e desduplicação
│   ├── services/                # Regras de negócio e exportadores
│   │   ├── exporters/           # Módulos de exportação (Excel)
│   │   └── audit_service.py     # Pipeline principal de execução da auditoria
│   ├── views/                   # Interface gráfica (GUI)
│   │   ├── assets/              # Ícones e imagens
│   │   ├── components/          # Componentes reutilizáveis da interface
│   │   ├── app_state.py         # Gerenciamento de estado da aplicação
│   │   └── app.py               # Janela principal (MainWindow)
│   ├── main.py                  # Ponto de entrada do sistema
│   └── path_manager.py          # Gerenciamento centralizado de caminhos da aplicação
├── tests/                       # Testes automatizados (pytest)
├── conftest.py                  # Configurações de testes
├── main.py                      # Atalho/Ponto de entrada raiz
└── requirements.txt             # Dependências do projeto
```

---

## 🛠️ Requisitos e Tecnologias

* **Linguagem:** Python 3.10+
* **Principais Bibliotecas:**
  * `customtkinter` — Interface gráfica moderna.
  * `pandas` — Estruturação e manipulação de tabelas de dados.
  * `duckdb` — Banco de dados analítico OLAP em memória.
  * `Pillow (PIL)` — Manipulação de imagens e ícones na interface.
  * `openpyxl` — Geração e formatação de planilhas Excel.
  * `tkinterdnd2` *(opcional)* — Suporte a arrastar e soltar arquivos na interface.

---

## 🔧 Configuração e Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/TRM-analises.git
   cd TRM-analises
   ```

2. **Crie e ative um ambiente virtual:**
   * **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python main.py
   ```

---

## ⚙️ Fluxo de Funcionamento

1. **Seleção de Modos e Arquivos:** O usuário seleciona o modo de auditoria (**SPED** ou **SINTEGRA**) na interface e informa os diretórios/arquivos correspondentes aos XMLs e livros fiscais.
2. **Parsing e Normalização:**
   * Os arquivos XML são lidos em paralelo.
   * Os arquivos de texto (SPED/Sintegra) são lidos com tratamento automático de codificação de texto (`utf-8`, `latin-1`, `utf-8-sig`).
3. **Desduplicação e Tratamento:** Os dados são inseridos no `FiscalRepository` e higienizados removendo duplicidades com base na Chave de Acesso ou na combinação de chave de negócio (CNPJ + Número do Documento + Modelo + Valor Total + Data de Emissão).
4. **Cruzamento SQL:** O `AuditService` carrega as tabelas resultantes (`df_xml` e `df_fiscal`) no **DuckDB** e executa a query SQL de conciliação (`sped_audit_query.sql` ou `sintegra_audit_query.sql`).
5. **Resultado e Exportação:** As métricas e inconsistências são exibidas em tela e podem ser exportadas para uma planilha Excel estruturada na pasta `outputs/`.

---

## 🛡️ Licença

Este projeto é um software proprietário desenvolvido para fluxos internos de análise e auditoria fiscal.