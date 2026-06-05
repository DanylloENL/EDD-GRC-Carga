# EDD-GRC-Carga

Pipeline automatizado em Python para processamento e carga em lote de equipamentos **EDD (Ethernet Dedicated Device)** no sistema **GRC (Gerência de Redes de Clientes)**.

O processo consolida dados de múltiplas fontes — inventário EDD, base SAIP e planta ativa do NOC — e gera os arquivos de carga prontos para importação no GRC, em lotes de até 500 linhas.

---

## Fluxo do Pipeline

```
[Inventário EDD]     [Base SAIP]
       |                  |
  Passo 1            Passo 1
01_tratamento_edd  02_tratamento_saip
       |                  |
       +--------+---------+
                |
           Passo 2/3
      03_compara_saip_edd
      (cruza SAIP x EDD)
                |
           Passo 4
  04_compara_planta_ativa_edd
  (filtra já cadastrados por nome e IP)
                |
           Passo 6
  05_tratamento_carga_lote_edd
  (gera: centro / equipamento / interface)
                |
           Passo 7
           06_divide
  (divide em lotes de 500 linhas)
                |
       [Upload para o GRC]
```

---

## Scripts

| Script | Descrição |
|---|---|
| `01_tratamento_edd.py` | Processa o relatório de inventário EDD: filtra por modelo e mês, exporta CSV limpo |
| `02_tratamento_saip.py` | Pré-processa o extrator SAIP (TXT → CSV): remove linhas corrompidas e colunas desnecessárias |
| `03_compara_saip_edd.py` | Cruza a base SAIP com o inventário EDD via `DESIGNACAO_ACESSO`, identificando status e IP de cada circuito |
| `04_compara_planta_ativa_edd.py` | Compara com a planta ativa do NOC por **nome** e por **IP**, marcando o que já está cadastrado no sistema |
| `05_tratamento_carga_lote_edd.py` | Gera os 3 arquivos de carga para o GRC: `centro.csv`, `equipamento.csv` e `interface.csv` |
| `06_divide.py` | Divide os arquivos de carga em lotes de 500 linhas, organizados por subpasta |

---

## Estrutura de Pastas

```
EDD-GRC-Carga/
├── scripts/
│   ├── 01_tratamento_edd.py
│   ├── 02_tratamento_saip.py
│   ├── 03_compara_saip_edd.py
│   ├── 04_compara_planta_ativa_edd.py
│   ├── 05_tratamento_carga_lote_edd.py
│   └── 06_divide.py
├── recursos/              ← Arquivos de referência (não versionados)
│   └── PORT_extrator_centro.csv
├── output/                ← Arquivos gerados (não versionados)
│   ├── passo1/
│   ├── passo2/
│   ├── passo3/
│   ├── passo4/
│   ├── passo6/
│   └── passo7/
│       ├── centro/
│       ├── equipamento/
│       └── interface/
├── .gitignore
└── README.md
```

---

## Requisitos

- Python 3.8+
- pandas

```bash
pip install pandas
```

---

## Como Usar

Execute os scripts em ordem a partir da raiz do projeto:

```bash
# Passo 1 — Tratar fontes brutas
python scripts/01_tratamento_edd.py
python scripts/02_tratamento_saip.py

# Passo 3 — Cruzar SAIP com EDD
python scripts/03_compara_saip_edd.py

# Passo 4 — Filtrar já cadastrados na planta ativa
python scripts/04_compara_planta_ativa_edd.py

# Passo 6 — Gerar arquivos de carga
python scripts/05_tratamento_carga_lote_edd.py

# Passo 7 — Dividir em lotes de 500 linhas
python scripts/06_divide.py
```

Após a execução, os arquivos prontos para upload no GRC estarão em:

```
output/passo7/centro/        → lotes de centros novos
output/passo7/equipamento/   → lotes de equipamentos
output/passo7/interface/     → lotes de interfaces
```

---

## Destaques Técnicos

- **Deduplicação inteligente:** centros são deduplicados por `sigla_centro` antes da carga, evitando o erro *"CONTATO 1 já cadastrado"* no GRC.
- **Dupla verificação de existência:** o script `04` cruza por nome de equipamento **e** por IP, eliminando cadastros duplicados mesmo quando o nome diverge.
- **Filtro de centros existentes:** o script `05` compara com a base exportada do GRC (`PORT_extrator_centro.csv`) e exclui automaticamente centros já registrados.
- **Sanitização de nomes:** caracteres inválidos (`(`, `)`, espaços, etc.) são removidos dos campos `sigla_centro` e `nome_eqpto` para garantir compatibilidade com as regras do GRC.
- **Lotes de 500 linhas:** respeitando o limite de upload do sistema.

---

## Observações

Os arquivos de dados (CSVs de entrada, saída e referência) não são versionados por conterem informações sensíveis da operação de rede. A estrutura de pastas é mantida via arquivos `.gitkeep`.
