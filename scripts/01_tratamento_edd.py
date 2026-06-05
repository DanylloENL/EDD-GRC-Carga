import pandas as pd
import datetime as dt

# --- CONFIGURAÇÕES ---
# Altere este número para o mês que você quer analisar (1=Janeiro, 12=Dezembro)
mes_desejado = 9
# ---------------------

# Caminho do arquivo de entrada
file_path = r"Device Inventory Report-20250918-102830_1579171642.csv"

# Carrega o arquivo CSV
df = pd.read_csv(file_path, sep=',', encoding='utf-8')

# --- INÍCIO DO TRATAMENTO ---

# Converte a coluna de data/hora
df['Last Update'] = pd.to_datetime(df['Last Update'])

# Dicionário com os tipos de dados para as outras colunas
dtypes_to_change = {
    'Device ID': 'str',
    'Dev No': 'str',
    'Serial': 'str',
    'Hostname': 'str',
    'Device Model': 'str',
    'Hardware Version': 'str',
    'Firmware Version': 'str',
    'Status': 'str',
    'Mismatch': 'str',
    'Links Number': 'Int64'
}
df = df.astype(dtypes_to_change)

# Remove as colunas que não são necessárias.
columns_to_drop = [
    'Notes', 'Address', 'Project Id', 'Country', 'State',
    'City', 'Station', 'Room', 'Shelf'
]
df = df.drop(columns=columns_to_drop)

# Filtra o DataFrame para o mês desejado (usando a variável de configuração)
print(f"Filtrando dados para o mês: {mes_desejado}...")
df = df[df['Last Update'].dt.month == mes_desejado]

# Filtra o DataFrame para manter apenas as linhas do ano corrente.
current_year = dt.datetime.now().year
df = df[df['Last Update'].dt.year == current_year]

# Filtra para remover linhas onde a coluna 'Location' contém a string "Vivax".
df = df[~df['Location'].str.contains("Vivax", na=False)]

# Filtra pelos modelos de dispositivo específicos.
device_models_to_keep = [
    "DM2104G2 - EDD E1 S.II",
    "DM2104G2 - EDD WRI",
    "DmSwitch 2104G1 - EDD (SERIES II)",
    "DmSwitch 2104G1 series II",
    "DmSwitch 2104G2 - EDD (SERIES II)",
    "DmSwitch 2104G2-EDD"
]
df = df[df['Device Model'].isin(device_models_to_keep)]

# --- FINALIZAÇÃO E EXPORTAÇÃO ---

# Verifica se o DataFrame resultante está vazio antes de salvar
if df.empty:
    print("\nNenhum dado encontrado para os filtros aplicados. O arquivo não será gerado.")
else:
    # Mapeamento do número do mês para o nome em português (minúsculas)
    nomes_meses = {
        1: "janeiro", 2: "fevereiro", 3: "marco", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }

    # Pega o nome do mês a partir do número. Se não encontrar, usa o próprio número.
    nome_mes = nomes_meses.get(mes_desejado, f"mes_{mes_desejado}")

    # Cria o nome do arquivo dinamicamente
    nome_arquivo_saida = f"edd_{nome_mes}.csv"

    # Exibe informações do resultado
    print("\nPrévia do DataFrame resultante:")
    print(df.head())
    print("\nInformações do DataFrame final:")
    df.info()

    # Salva o resultado em um novo arquivo CSV com o nome dinâmico
    df.to_csv(nome_arquivo_saida, index=False, encoding='utf-8-sig')
    print(f"\nArquivo salvo com sucesso como: {nome_arquivo_saida}")