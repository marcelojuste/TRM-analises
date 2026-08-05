# Diretrizes do Gemini - Sistema de Auditoria Fiscal

Este documento contém os mandatos fundamentais e as regras de precedência absoluta que regem a conduta e as respostas do Gemini neste repositório.

## 🚨 Mandatos de Precedência Absoluta

1. **Idioma de Resposta**:
   * **Todas as respostas, explicações, soluções, diagnósticos de erro e orientações do Gemini devem ser fornecidos exclusivamente em Português (Brasil).**
   * O código gerado deve manter nomes de variáveis, classes e funções em inglês, mas comentários explicativos ou documentação associada devem estar em português.

2. **Fidelidade Estrita à Tech Stack**:
   * O projeto é um executável desktop Windows 100% local, de baixa complexidade e alta manutenibilidade.
   * **Linguagem**: Python 3.11+.
   * **Banco de Dados**: DuckDB para processamento analítico com SQL puro (NÃO usar ORMs como SQLAlchemy, SQLModel, etc.).
   * **Armazenamento de Logs**: TinyDB para persistência de relatórios e divergências em formato JSON.
   * **Interface Gráfica (GUI)**: CustomTkinter (NÃO sugerir web-views, Electron ou outros toolkits pesados).
   * **Parsers Nativos**: Ingestão de XML com `xml.etree.ElementTree` e SPED TXT com `open()` nativo. É **expressamente proibido** o uso de Pandas, Polars ou similares para manipulação de dados para evitar estouro de memória e dependências desnecessárias.
   * **Compilação**: PyInstaller com empacotamento `--onefile`.

3. **Arquitetura em Camadas (Layered Monolith)**:
   * Todo código deve ser organizado estritamente na estrutura definida sob `src/`:
     * `src/presentation/` (GUI)
     * `src/services/` (Orquestração e lógica de auditoria)
     * `src/parsers/` (Leitura XML/TXT)
     * `src/database/` (SQL e DuckDB)
     * `src/loggers/` (TinyDB)

---

## 💻 Comandos e Operações do Projeto

### Instalação e Execução
* Configurar ambiente virtual: `python -m venv .venv`
* Instalar dependências: `python -m pip install -r requirements.txt`
* Executar em desenvolvimento: `python src/main.py`

### Qualidade e Testes
* Rodar testes: `pytest`
* Assegurar que qualquer correção de bug ou nova feature venha acompanhada de testes robustos.

### Geração de Executável
* Comando do PyInstaller:
  `pyinstaller --noconfirm --onedir --windowed --name "AuditoriaFiscal" src/main.py`

---

## 🎨 Padrões de Código e Boas Práticas
* **Tipagem de dados**: Usar `typing` do Python para assinaturas de métodos (`def processar_dados(caminho: str) -> dict:`).
* **Parâmetros SQL**: Sempre usar consultas parametrizadas com DuckDB (ex: `conn.execute("SELECT * FROM tabelas WHERE id = ?", (id_val,))`) para evitar brechas de segurança.
* **Manutenibilidade**: Código limpo, modular e aderente ao princípio de responsabilidade única para cada camada da arquitetura monolítica.
