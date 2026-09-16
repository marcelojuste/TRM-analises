# Diretrizes do Gemini - Sistema de Auditoria Fiscal

Este documento contém os mandatos fundamentais e as regras de precedência absoluta que regem a conduta e as respostas do Gemini neste repositório.

## 🚨 Mandatos de Precedência Absoluta

1. **Idioma de Resposta**:
   * **Todas as respostas, explicações, soluções, diagnósticos de erro e orientações do Gemini devem ser fornecidos exclusivamente em Português (Brasil).**
   * O código gerado deve manter nomes de variáveis, classes e funções em inglês, mas comentários explicativos ou documentação associada devem estar em português.

2. **Fidelidade Estrita à Tech Stack e Alvo Hardware**:
   * O projeto é um executável desktop Windows 100% local, de baixa complexidade, otimizado para **computadores com recursos limitados (Windows 7 / 4 GB de RAM)**.
   * **Linguagem**: Python (compatível com o ambiente alvo; Python 3.11+ exige atenção aos patches do Windows 7).
   * **Banco de Dados**: DuckDB para processamento analítico com SQL puro e capacidade *out-of-core*. **Obrigatório definir travas explícitas de RAM** (`max_memory = '512MB'`, `threads = 2`, `temp_directory`).
   * **Armazenamento de Logs**: TinyDB para persistência de relatórios e divergências em formato JSON.
   * **Interface Gráfica (GUI)**: CustomTkinter (NÃO sugerir web-views, Electron ou outros toolkits pesados).
   * **Parsers Nativos em Streaming**: Ingestão de XML com `xml.etree.ElementTree.iterparse` (liberando memória nó a nó via `elem.clear()`) e SPED TXT com `open()` nativo usando geradores (`yield`) ou importação direta no DuckDB. É **expressamente proibido** o uso de Pandas, Polars ou similares.
   * **Compilação**: PyInstaller exclusivamente com empacotamento **`--onedir`** (NÃO usar `--onefile` para evitar picos de uso de CPU/RAM durante descompactação temporária em HDs antigos).

3. **Arquitetura em Camadas (Layered Monolith)**:
   * Todo código deve ser organizado estritamente na estrutura definida sob `src/`:
     * `src/presentation/` (GUI)
     * `src/services/` (Orquestração e lógica de auditoria)
     * `src/parsers/` (Leitura XML/TXT via streaming)
     * `src/database/` (SQL puro e DuckDB)
     * `src/loggers/` (TinyDB)

---

## 💻 Comandos e Operações do Projeto

### Instalação e Execução
* Configurar ambiente virtual: `python -m venv .venv`
* Instalar dependências: `python -m pip install -r requirements.txt`
* Executar em desenvolvimento: `python src/main.py`

### Qualidade e Testes
* Rodar testes: `pytest`
* Assegurar que qualquer correção de bug ou nova feature venha acompanhada de testes robustos utilizando `pytest`.

### Geração de Executável
* Comando do PyInstaller:
  `pyinstaller --noconfirm --onedir --windowed --name "AuditoriaFiscal" src/main.py`

---

## 🎨 Padrões de Código e Boas Práticas
* **Tipagem de dados**: Usar `typing` do Python para assinaturas de métodos (`def processar_dados(caminho: str) -> dict:`).
* **Parâmetros SQL**: Sempre usar consultas parametrizadas com DuckDB (ex: `conn.execute("SELECT * FROM tabelas WHERE id = ?", (id_val,))`) para evitar brechas de segurança e garantir o aproveitamento de índices/caches.
* **Manutenibilidade e Performance**: Código limpo, modular e com garantia de consumo de memória $O(1)$ na fase de ingestão.
