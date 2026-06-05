import pandas as pd
import os
import glob

def analisar_e_trazer_status(arquivo_saip, arquivo_edd, arquivo_saida):
    """
    Analisa dois arquivos CSV e, ao encontrar uma correspondência, traz o
    status do arquivo de referência em vez de apenas marcar 'Sim'.

    Args:
        arquivo_saip (str): Caminho para o arquivo SAIP.
        arquivo_edd (str): Caminho para o arquivo de referência EDD.
        arquivo_saida (str): Caminho para o arquivo de saída.
    """
    try:
        # 1. Carrega os arquivos CSV
        saip_df = pd.read_csv(arquivo_saip, delimiter=';', encoding='utf-8')
        edd_df = pd.read_csv(arquivo_edd, delimiter=';', encoding='utf-8')

        # --- Processo de Normalização e Junção ---

        # 2. Normaliza as colunas de chave para uma junção confiável
        saip_df['chave_saip'] = saip_df['DESIGNACAO_ACESSO'].astype(str).str.lower().str.strip()
        edd_df['chave_edd'] = edd_df['Desig Acesso'].astype(str).str.lower().str.strip()

        # 3. Prepara um DataFrame de mapeamento com a chave e os valores a serem trazidos ('Status' e 'IP')
        #    Removemos duplicatas na chave para evitar linhas duplicadas no resultado final.
        map_df = edd_df[['chave_edd', 'Status', 'IP']].drop_duplicates(subset=['chave_edd'])

        # 4. Realiza uma junção à esquerda (left merge)
        #    Isso mantém todas as linhas do saip_df e adiciona as colunas 'Status' e 'IP' onde as chaves correspondem.
        resultado_df = pd.merge(
            saip_df,
            map_df,
            left_on='chave_saip',
            right_on='chave_edd',
            how='left'
        )

        # --- Limpeza e Finalização ---

        # 5. Renomeia as novas colunas para algo mais específico
        resultado_df = resultado_df.rename(columns={'Status': 'Status_EDD', 'IP': 'IP_EDD'})

        # 6. Preenche os valores não encontrados com 'Nao encontrado'
        resultado_df['Status_EDD'] = resultado_df['Status_EDD'].fillna('Nao encontrado')
        resultado_df['IP_EDD'] = resultado_df['IP_EDD'].fillna('Nao encontrado')

        # 7. Remove as colunas de chave temporárias
        resultado_df = resultado_df.drop(columns=['chave_saip', 'chave_edd'])

        # 8. Salva o resultado
        resultado_df.to_csv(arquivo_saida, index=False, sep=';')

        print(f"Análise concluída com sucesso! O arquivo '{arquivo_saida}' foi gerado.")

    except FileNotFoundError as e:
        print(f"Erro: O arquivo {e.filename} não foi encontrado.")
    except KeyError as e:
        print(f"Erro: A coluna {e} não foi encontrada em um dos arquivos.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

def comparar_com_noc(arquivo_resultado, arquivo_noc, arquivo_saida_final):
    """
    Compara o arquivo de resultado com o arquivo NOC usando a coluna de acesso.
    Adiciona uma coluna indicando se o acesso está presente no NOC.

    Args:
        arquivo_resultado (str): Caminho para o arquivo gerado pela análise.
        arquivo_noc (str): Caminho para o arquivo NOC.
        arquivo_saida_final (str): Caminho para o arquivo final de saída.
    """
    try:
        resultado_df = pd.read_csv(arquivo_resultado, delimiter=';', encoding='utf-8')
        noc_df = pd.read_csv(arquivo_noc, delimiter=';', encoding='utf-8')

        # Normaliza as colunas para comparação
        resultado_df['acesso_normalizado'] = resultado_df['DESIGNACAO_ACESSO'].astype(str).str.lower().str.strip()
        noc_df['acesso_noc_normalizado'] = noc_df['inf_acesso_desig'].astype(str).str.lower().str.strip()

        # Marca se o acesso está presente no NOC
        resultado_df['Presente_no_NOC'] = resultado_df['acesso_normalizado'].isin(noc_df['acesso_noc_normalizado'])
        resultado_df['Presente_no_NOC'] = resultado_df['Presente_no_NOC'].map({True: 'Sim', False: 'Não'})

        # Remove coluna temporária
        resultado_df = resultado_df.drop(columns=['acesso_normalizado'])

        # Salva o arquivo final
        resultado_df.to_csv(arquivo_saida_final, index=False, sep=';')
        print(f"Comparação com NOC concluída! Arquivo '{arquivo_saida_final}' gerado.")

    except Exception as e:
        print(f"Erro na comparação com NOC: {e}")

def analisar_e_trazer_status_saip(arquivo_saip, arquivo_edd, arquivo_saida):
    """
    Analisa arquivos de alarmes e, ao encontrar uma correspondência, traz o
    status do arquivo de referência em vez de apenas marcar 'Sim'.

    Args:
        arquivo_saip (str): Caminho para o arquivo de alarmes.
        arquivo_edd (str): Caminho para o arquivo de referência EDD.
        arquivo_saida (str): Caminho para o arquivo de saída.
    """
    try:
        # 1. Carrega os arquivos CSV
        alarmes_df = pd.read_csv(arquivo_saip, delimiter=';', encoding='utf-8')
        edd_df = pd.read_csv(arquivo_edd, delimiter=',', encoding='utf-8-sig')

        # 2. Normaliza as colunas de chave para uma junção confiável
        alarmes_df['chave_saip'] = alarmes_df['DESIGNACAO_ACESSO'].astype(str).str.lower().str.strip()
        edd_df['chave_edd'] = edd_df['Device ID'].astype(str).str.lower().str.strip()

        # 3. Prepara um DataFrame de mapeamento com a chave e os valores a serem trazidos ('Status' e 'IP')
        map_df = edd_df[['chave_edd', 'Status', 'Hostname']].drop_duplicates(subset=['chave_edd'])

        # 4. Realiza uma junção à esquerda (left merge)
        resultado_df = pd.merge(
            alarmes_df,
            map_df,
            left_on='chave_saip',
            right_on='chave_edd',
            how='left'
        )

        # 5. Renomeia as novas colunas para algo mais específico
        resultado_df = resultado_df.rename(columns={'Status': 'Status_EDD', 'Hostname': 'IP_EDD'})

        # 6. Preenche os valores não encontrados com 'Não encontrado'
        resultado_df['Status_EDD'] = resultado_df['Status_EDD'].fillna('Não encontrado')
        resultado_df['IP_EDD'] = resultado_df['IP_EDD'].fillna('Não encontrado')

        # 7. Substitui 'Normal' por 'ENCONTRADO' para melhor visualização
        resultado_df['Status_EDD'] = resultado_df['Status_EDD'].replace('Normal', 'ENCONTRADO')

        # 8. Remove as colunas de chave temporárias
        resultado_df = resultado_df.drop(columns=['chave_saip', 'chave_edd'])

        # 8. Salva o resultado
        resultado_df.to_csv(arquivo_saida, index=False, sep=';')

        print(f"Análise concluída com sucesso! O arquivo '{arquivo_saida}' foi gerado.")

    except FileNotFoundError as e:
        print(f"Erro: O arquivo {e.filename} não foi encontrado.")
    except KeyError as e:
        print(f"Erro: A coluna {e} não foi encontrada em um dos arquivos.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Execução do Script ---
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    passo1_dir = os.path.join(script_dir, "output", "passo1")
    passo2_dir = os.path.join(script_dir, "output", "passo2")
    os.makedirs(passo2_dir, exist_ok=True)

    arquivo_saip = os.path.join(passo1_dir, "saip.csv")

    arquivos_edd = glob.glob(os.path.join(passo1_dir, "edd_*.csv"))
    arquivos_edd = [f for f in arquivos_edd if "nao_padrao" not in f]
    if not arquivos_edd:
        raise FileNotFoundError(f"Nenhum arquivo edd_*.csv encontrado em: {passo1_dir}")
    arquivo_edd = max(arquivos_edd, key=os.path.getmtime)

    arquivo_saida = os.path.join(passo2_dir, "saip_edd_comparado.csv")

    print(f"SAIP:  {arquivo_saip}")
    print(f"EDD:   {arquivo_edd}")
    analisar_e_trazer_status_saip(arquivo_saip, arquivo_edd, arquivo_saida)