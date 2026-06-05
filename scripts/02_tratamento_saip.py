import pandas as pd
import csv
import os

# --- A SOLUÇÃO ESTÁ AQUI ---
# Aumenta o limite de tamanho do campo do CSV para um valor bem grande (ex: 1MB)
# Isso permite que o script leia linhas corrompidas que são extremamente longas.
csv.field_size_limit(1000000)
# -----------------------------

# 1. Definir os caminhos dos arquivos
file_path_in = r"extrator004.txt"
file_path_out = r"extrator004_tratado.csv"
file_path_exceptions = r"extrator004_excecoes.csv"
file_path_good_temp = r"extrator004_linhas_validas_temp.csv"

# --- ETAPA 1: PRÉ-PROCESSAMENTO COM PYTHON PURO ---

print("Iniciando pré-processamento do arquivo...")
good_lines_count = 0
bad_lines_count = 0

try:
    with open(file_path_in, 'r', encoding='latin-1', newline='') as infile, \
         open(file_path_good_temp, 'w', encoding='utf-8', newline='') as good_file, \
         open(file_path_exceptions, 'w', encoding='utf-8', newline='') as bad_file:

        reader = csv.reader(infile, delimiter=';')
        writer_good = csv.writer(good_file, delimiter=';')
        writer_bad = csv.writer(bad_file, delimiter=';')

        try:
            header = next(reader)
            EXPECTED_COLUMNS = len(header)
            writer_good.writerow(header)
            print(f"Cabeçalho identificado com {EXPECTED_COLUMNS} colunas.")
        except StopIteration:
            print("Erro: Arquivo de entrada está vazio.")
            exit() # Sai do script se o arquivo estiver vazio

        for row in reader:
            if len(row) == EXPECTED_COLUMNS:
                writer_good.writerow(row)
                good_lines_count += 1
            else:
                writer_bad.writerow(row)
                bad_lines_count += 1
    
    print(f"Pré-processamento concluído.")
    print(f" - {good_lines_count} linhas válidas salvas em arquivo temporário.")
    print(f" - {bad_lines_count} linhas de exceção salvas em '{file_path_exceptions}'")

    if good_lines_count == 0:
        print("Nenhuma linha válida encontrada. O arquivo de saída não será gerado.")
        exit()

    # --- ETAPA 2: PROCESSAMENTO COM PANDAS (AGORA COM O ARQUIVO LIMPO) ---
    
    print("\nIniciando processamento com pandas no arquivo limpo...")
    df = pd.read_csv(file_path_good_temp, sep=';', encoding='utf-8')

    columns_to_remove = [
        "PRODUTO", "CONTA_CORRENTE", "DESIGNACAO_ACESSO_REDUNDANTE",
        "DATA_ALOCACAO", "RESPONSAVEL_ALOCACAO", "DATA_ATIVACAO",
        "RESPONSAVEL_ATIVACAO", "DESIGNACAO_E1", "FACILIDADE_E1",
        "TELLABS", "DATACOM", "CONVERSOR_DE_PROTOCOLO", "PROTOCOLO_L2",
        "COMBO_VIP", "LINK_ACESSO", "MULTILINK_CAD", "MULTILINK_ATV",
        "QOS", "OBSERVACAO", "", "_1"
    ]
    
    cols_to_drop_existing = [col for col in columns_to_remove if col in df.columns]

    df_final = df.drop(columns=cols_to_drop_existing)

    df_final.to_csv(
        file_path_out,
        sep=';',
        index=False,
        encoding='utf-8-sig'
    )

    print(f"\nArquivo tratado com sucesso e salvo em: '{file_path_out}'")
    print("\nPrévia dos dados tratados:")
    print(df_final.head())

finally:
    # --- ETAPA 3: LIMPEZA ---
    if os.path.exists(file_path_good_temp):
        os.remove(file_path_good_temp)
        print(f"\nArquivo temporário '{file_path_good_temp}' removido.")