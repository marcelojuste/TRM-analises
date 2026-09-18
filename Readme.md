# TRM Análises — Fiscal Audit Tool

Ferramenta modular de **alta performance e baixo consumo de memória** para extração, consolidação e auditoria cruzada de documentos fiscais eletrônicos, com suporte a **NF-e, NFC-e e arquivos SPED Fiscal**.

O projeto foi desenvolvido para processar grandes volumes de dados fiscais em ambientes com recursos extremamente limitados, incluindo máquinas com **Windows 7 e apenas 4 GB de RAM**.

A arquitetura prioriza:

* Processamento **streaming**, evitando carregar arquivos inteiros em memória.
* Persistência analítica eficiente utilizando **DuckDB**.
* Estruturas de dados otimizadas para reduzir overhead de objetos Python.
* Escrita no banco em **lotes (batch)**.
* Componentização por responsabilidades.
* Testabilidade através de testes unitários isolados.

> **Meta de arquitetura:** manter o consumo de memória da aplicação abaixo de **1 GB de RAM**, mesmo durante o processamento de grandes volumes de documentos fiscais.

---

## 🚀 Principais Características

| Característica           | Implementação                             |
| ------------------------ | ----------------------------------------- |
| Linguagem                | Python 3.10+                              |
| Banco analítico          | DuckDB                                    |
| Processamento XML        | `xml.etree.ElementTree.iterparse`         |
| Persistência             | Repository Pattern                        |
| Escrita no banco         | Batching + `executemany`                  |
| Modelos                  | `dataclass(slots=True)`                   |
| Roteamento de campos XML | Dispatch Table                            |
| Testes                   | pytest                                    |
| Foco                     | Performance + baixo consumo de RAM        |
| Ambiente-alvo            | Windows 7+ / máquinas com poucos recursos |

---

## 🏗️ Arquitetura

O sistema foi estruturado em camadas independentes, permitindo que cada componente tenha uma responsabilidade bem definida.

```text
                    ┌─────────────────────┐
                    │   Arquivos Fiscais  │
                    │                     │
                    │ XML / SPED Fiscal   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Parsers       │
                    │                     │
                    │ XML Streaming       │
                    │ SPED                │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FiscalDocument    │
                    │                     │
                    │ dataclass + slots   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ FiscalRepository    │
                    │                     │
                    │ Batch / Flush       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       DuckDB        │
                    │                     │
                    │ OLAP / Analytics    │
                    └─────────────────────┘
```

### Fluxo de processamento

```text
Arquivo
   │
   ▼
Leitura Streaming
   │
   ▼
Extração dos dados
   │
   ▼
FiscalDocument
   │
   ▼
Buffer em memória
   │
   ├── batch_size atingido
   │
   ▼
executemany()
   │
   ▼
DuckDB
   │
   ▼
Próximo lote
```

O processamento é deliberadamente orientado a **fluxo**, evitando a criação de grandes estruturas intermediárias contendo todos os documentos.

---

# 📁 Estrutura do Projeto

```text
TRM-analises/
│
├── src/
│   │
│   ├── database/
│   │   └── # Conexão e gerenciamento do lifecycle do DuckDB
│   │
│   ├── models/
│   │   └── # Modelos de domínio
│   │      └── FiscalDocument
│   │
│   ├── parsers/
│   │   ├── # Parser streaming de XML
│   │   ├── # Dispatch Table
│   │   └── # Parser de arquivos SPED
│   │
│   └── repositories/
│       └── # Persistência em lote
│          └── FiscalRepository
│
├── tests/
│   └── # Testes unitários com pytest
│
├── pyproject.toml
│   └── # Configurações do projeto e ferramentas
│
├── requirements.txt
│   └── # Dependências da aplicação
│
└── README.md
```

## Responsabilidade dos módulos

### `src/database`

Responsável pela criação, configuração e gerenciamento das conexões DuckDB.

O módulo também centraliza o lifecycle da conexão para evitar conexões espalhadas pela aplicação.

---

### `src/models`

Contém os modelos utilizados durante o processamento.

O principal modelo é:

```python
FiscalDocument
```

Os objetos utilizam:

```python
@dataclass(slots=True)
```

O uso de `slots` reduz o overhead associado ao armazenamento de atributos dos objetos, sendo especialmente importante quando milhares ou milhões de registros são processados.

---

### `src/parsers`

Responsável pela leitura e interpretação dos documentos fiscais.

Inclui:

* Parser de XML;
* Processamento streaming;
* Extração de campos;
* Dispatch Table;
* Parser de SPED Fiscal.

Os parsers devem produzir dados progressivamente, evitando acumular documentos desnecessariamente em memória.

---

### `src/repositories`

Responsável pela persistência dos dados.

O principal componente é:

```text
FiscalRepository
```

O repository utiliza um buffer interno e realiza o `flush` quando o número de registros atinge o `batch_size`.

Isso evita realizar uma operação de INSERT para cada documento.

---

### `tests`

Contém os testes automatizados do projeto.

Os testes utilizam `pytest` e devem priorizar:

* isolamento;
* execução rápida;
* bancos DuckDB em memória;
* arquivos XML/SPED pequenos e controlados;
* validação independente dos parsers e repositories.

---

# 🧠 Decisões de Arquitetura

## 1. Streaming XML

Arquivos XML fiscais podem atingir tamanhos consideráveis e podem existir em grandes quantidades.

Por isso, o projeto utiliza:

```python
xml.etree.ElementTree.iterparse
```

em vez de carregar o XML inteiro com:

```python
ET.parse(...)
```

O processamento ocorre progressivamente conforme os elementos são lidos.

### Limpeza de memória

Após o processamento de um elemento, sua árvore é liberada:

```python
elem.clear()
```

Quando necessário, a raiz também pode ser limpa:

```python
root.clear()
```

Exemplo conceitual:

```python
for event, elem in ET.iterparse(file, events=("end",)):
    if elem.tag == "det":
        process_element(elem)

    elem.clear()
```

Isso evita o crescimento contínuo da árvore XML na memória.

### Objetivo

```text
Memória ≈ O(tamanho do elemento atualmente processado)
```

em vez de:

```text
Memória ≈ O(tamanho completo do XML)
```

> **Regra:** nunca transformar um grande conjunto de XMLs em uma lista de árvores XML completas.

---

# ⚡ 2. Pattern Dispatch Table

Em vez de utilizar longas cadeias de:

```python
if tag == "x":
    ...
elif tag == "y":
    ...
elif tag == "z":
    ...
```

o projeto utiliza uma tabela de despacho.

Exemplo:

```python
FIELD_HANDLERS = {
    "nNF": handle_number,
    "dhEmi": handle_issue_date,
    "CNPJ": handle_cnpj,
    "xNome": handle_name,
}
```

A resolução ocorre através de uma consulta ao dicionário:

```python
handler = FIELD_HANDLERS.get(tag)
```

Isso mantém o código mais modular e facilita a inclusão de novos campos sem aumentar uma cadeia de condicionais.

---

# 📦 3. Repository Pattern + Batch

A persistência é centralizada no:

```python
FiscalRepository
```

O repository funciona como um **Context Manager**:

```python
with FiscalRepository(connection, batch_size=1000) as repository:
    ...
```

Os registros são acumulados temporariamente:

```text
Registro 1
Registro 2
Registro 3
...
Registro N
```

Quando o limite é atingido:

```text
buffer >= batch_size
       │
       ▼
    flush()
       │
       ▼
executemany()
       │
       ▼
DuckDB
       │
       ▼
buffer liberado
```

Isso reduz a quantidade de operações individuais realizadas contra o banco.

---

# 🧱 4. Estruturas de Dados Otimizadas

O modelo de domínio utiliza:

```python
@dataclass(slots=True)
class FiscalDocument:
    ...
```

O `slots=True` evita a criação de um `__dict__` por instância, reduzindo o overhead de memória.

Isso é particularmente relevante em um sistema que pode processar uma quantidade muito grande de documentos.

---

# 🦆 DuckDB

O DuckDB é utilizado como motor analítico do projeto.

Ele é adequado para consultas OLAP e análises sobre grandes volumes de dados, mantendo a arquitetura simples e evitando a necessidade de um servidor de banco de dados externo.

Exemplos de análises que podem ser realizadas:

* cruzamento de NF-e/NFC-e;
* comparação entre XML e SPED;
* identificação de documentos ausentes;
* auditoria fiscal;
* validação de registros;
* análise de entradas e saídas;
* conferência de chaves de acesso;
* identificação de inconsistências.

---

# 🔧 Instalação

## Requisitos

* Python **3.10 ou superior**
* Windows 7 ou superior
* Pelo menos 4 GB de RAM para o ambiente mínimo
* Git, caso o projeto seja obtido através de um repositório Git

---

## 1. Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd TRM-analises
```

---

## 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv venv
```

---

## 3. Ativar o ambiente virtual

```powershell
.\venv\Scripts\activate
```

Após a ativação, o terminal deverá apresentar algo semelhante a:

```text
(venv) C:\Projetos\TRM-analises>
```

---

## 4. Atualizar o pip

```bash
python -m pip install --upgrade pip
```

---

## 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

# 🧪 Testes

O projeto utiliza **pytest** para os testes automatizados.

Com o ambiente virtual ativado:

```bash
python -m pytest
```

Para obter uma saída mais detalhada:

```bash
python -m pytest -v
```

Para executar um arquivo específico:

```bash
python -m pytest tests/test_parser.py
```

Para executar um teste específico:

```bash
python -m pytest tests/test_parser.py::test_nome_do_teste
```

---

# 💻 Exemplo Prático

O fluxo esperado é:

```text
XML
 ↓
Parser Streaming
 ↓
FiscalDocument
 ↓
FiscalRepository
 ↓
Batch
 ↓
DuckDB
```

Exemplo:

```python
from src.parsers.xml_parser import XMLParser
from src.repositories.fiscal_repository import FiscalRepository


def process_xml(file_path, connection):
    parser = XMLParser()

    with FiscalRepository(
        connection,
        batch_size=1000,
    ) as repository:

        for document in parser.parse(file_path):
            repository.add(document)
```

A utilização do `with` garante que o repository possa executar o `flush` final antes de encerrar o processamento.

Um fluxo equivalente para vários arquivos pode seguir o mesmo princípio:

```python
for xml_file in xml_files:

    for document in parser.parse(xml_file):
        repository.add(document)
```

O ponto importante é que os documentos são processados **progressivamente**, em vez de serem acumulados em uma lista gigante.

---

# 🧮 Estratégia de Batch

O `batch_size` deve ser configurável.

Exemplo:

```python
with FiscalRepository(
    connection,
    batch_size=1000,
) as repository:
    ...
```

Um batch menor:

```python
batch_size=500
```

pode reduzir o pico de memória.

Um batch maior:

```python
batch_size=5000
```

pode reduzir a quantidade de operações de escrita, mas aumenta o consumo temporário de memória.

Portanto, o tamanho ideal deve ser definido considerando:

* quantidade de registros;
* tamanho dos registros;
* RAM disponível;
* velocidade de armazenamento;
* custo das operações de escrita.

---

# 🧠 Diretrizes de Baixo Consumo de RAM

Este projeto possui **baixo consumo de memória como requisito arquitetural**, e não apenas como otimização posterior.

## ✅ Fazer

### Processar XML com `iterparse`

```python
ET.iterparse(...)
```

### Liberar elementos processados

```python
elem.clear()
```

### Utilizar `dataclass(slots=True)`

```python
@dataclass(slots=True)
```

### Persistir em lotes

```python
repository.add(document)
```

com `flush` periódico.

### Utilizar generators

Preferir:

```python
def parse():
    for item in items:
        yield item
```

em vez de:

```python
def parse():
    result = []

    for item in items:
        result.append(item)

    return result
```

### Processar arquivos um por vez

Sempre que possível:

```text
XML 1 → processa → libera
XML 2 → processa → libera
XML 3 → processa → libera
```

---

# 🚫 Evitar

## ❌ Não carregar todos os XMLs na memória

Evitar:

```python
documents = list(parser.parse_all(files))
```

em grandes volumes.

---

## ❌ Não construir uma árvore XML completa sem necessidade

Evitar:

```python
tree = ET.parse(file)
root = tree.getroot()
```

para arquivos grandes quando o processamento pode ser feito via streaming.

---

## ❌ Não acumular milhões de objetos Python

Evitar:

```python
documents = []

for document in parser.parse(file):
    documents.append(document)
```

---

## ❌ Não realizar INSERT individual

Evitar:

```python
for document in documents:
    connection.execute(
        "INSERT INTO fiscal_documents VALUES (...)"
    )
```

O repository deve agrupar registros e utilizar operações em lote.

---

## ❌ Não utilizar DataFrames como intermediários gigantes sem necessidade

Bibliotecas como Pandas são excelentes para análise, mas podem aumentar significativamente o consumo de RAM quando utilizadas como etapa intermediária para grandes volumes.

Sempre que possível:

```text
XML
 ↓
Parser streaming
 ↓
Repository
 ↓
DuckDB
```

em vez de:

```text
XML
 ↓
Lista gigante
 ↓
DataFrame gigante
 ↓
DuckDB
```

---

# 📊 Objetivo de Uso de Memória

A arquitetura busca manter o consumo da aplicação:

```text
< 1 GB RAM
```

mesmo em máquinas com:

```text
4 GB RAM
```

O consumo real depende de fatores como:

* tamanho dos XMLs;
* quantidade de arquivos simultaneamente processados;
* `batch_size`;
* consultas DuckDB executadas;
* tamanho dos registros;
* sistema operacional;
* outros processos executando na máquina.

O limite de memória deve, portanto, ser tratado como **objetivo arquitetural e métrica de validação**, e não como garantia independente das condições de execução.

---

# 🔍 Auditoria Fiscal

O objetivo final da ferramenta é permitir o cruzamento de diferentes fontes fiscais.

Exemplo conceitual:

```text
                 ┌─────────────┐
                 │    XML      │
                 │ NF-e/NFC-e  │
                 └──────┬──────┘
                        │
                        │
                chave de acesso
                        │
                        ▼
                 ┌─────────────┐
                 │   DuckDB    │
                 │             │
                 │   JOIN      │
                 └──────┬──────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        ┌───────────┐       ┌───────────┐
        │   SPED    │       │    XML    │
        │    IPI    │       │           │
        └───────────┘       └───────────┘
```

Isso permite identificar situações como:

* chave existente no XML e ausente no SPED;
* chave existente no SPED e ausente no XML;
* documentos presentes em ambas as fontes;
* divergências entre fontes;
* entradas e saídas;
* documentos que precisam de investigação.

---

# 🧪 Filosofia de Testes

Os testes devem acompanhar as fronteiras principais do sistema:

```text
Parser
  ↓
Model
  ↓
Repository
  ↓
DuckDB
```

Os testes devem priorizar cenários pequenos e determinísticos.

Exemplos:

```text
XML válido
XML com campos ausentes
XML com namespaces
Múltiplos documentos
Batch atingido
Flush final
Repository utilizado com with
Dados persistidos corretamente
```

Para testes de persistência, deve-se preferir DuckDB em memória quando o objetivo for isolamento e velocidade.

---

# 🔒 Princípios do Projeto

O desenvolvimento deve seguir alguns princípios fundamentais:

### Simplicidade

Evitar abstrações desnecessárias.

### Streaming

Processar dados conforme eles chegam.

### Batching

Escrever no banco em grupos.

### Baixo overhead

Reduzir objetos e estruturas temporárias.

### Separação de responsabilidades

Parser não deve ser responsável pela persistência.

Repository não deve interpretar XML.

Model não deve conhecer detalhes do banco.

### Testabilidade

Cada componente deve poder ser testado isoladamente.

---

# 📌 Checklist de Performance

Antes de adicionar uma nova funcionalidade, verificar:

* [ ] O código carrega arquivos inteiros na memória?
* [ ] É possível utilizar generator?
* [ ] O processamento pode ser feito via streaming?
* [ ] Elementos XML são liberados com `elem.clear()`?
* [ ] O código cria listas grandes desnecessariamente?
* [ ] A persistência está sendo realizada em lote?
* [ ] O `batch_size` é configurável?
* [ ] O modelo utiliza `slots=True` quando apropriado?
* [ ] A consulta DuckDB evita materializar dados desnecessariamente?
* [ ] Existe teste automatizado para o novo comportamento?

---

# 🛠️ Desenvolvimento

Para trabalhar no projeto:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Executar os testes:

```bash
python -m pytest
```

Executar com maior detalhamento:

```bash
python -m pytest -v
```

---

# 📜 Licença

Projeto desenvolvido para uso da **TRM Sistemas**.

A definição dos termos de distribuição, modificação e utilização deve ser estabelecida conforme a política de licenciamento do projeto.

---

# 📈 Visão de Arquitetura

O princípio central do **TRM Análises** pode ser resumido em:

```text
             GRANDES VOLUMES DE DADOS
                       │
                       ▼
              ┌─────────────────┐
              │    STREAMING    │
              │                 │
              │ XML / SPED      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  OBJETOS LEVES  │
              │                 │
              │ dataclass+slots │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     BATCH       │
              │                 │
              │     Flush       │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     DUCKDB      │
              │                 │
              │    ANALYTICS    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ AUDITORIA FISCAL│
              └─────────────────┘
```

> **TRM Análises** foi projetado para transformar grandes volumes de documentos fiscais em dados estruturados e auditáveis, mantendo a utilização de recursos previsível mesmo em ambientes computacionais restritos.
