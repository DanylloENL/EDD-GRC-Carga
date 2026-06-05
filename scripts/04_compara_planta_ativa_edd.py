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
        saip_df = pd.read_csv(arquivo_saip, delimiter=';', encoding='latin-1')
        edd_df = pd.read_csv(arquivo_edd, delimiter=';', encoding='utf-8')

        # --- Processo de Normalização e Junção ---

        # 2. Normaliza as colunas de chave para uma junção confiável
        saip_df['chave_saip'] = saip_df['acesso_desig'].astype(str).str.lower().str.strip()
        edd_df['chave_edd'] = edd_df['DESIGNACAO_ACESSO'].astype(str).str.lower().str.strip()

        # 3. Prepara um DataFrame de mapeamento com a chave e os valores a serem trazidos ('Status' e 'IP')
        #    Removemos duplicatas na chave para evitar linhas duplicadas no resultado final.
        map_df = edd_df[['chave_edd', 'Status_EDD', 'IP_EDD']].drop_duplicates(subset=['chave_edd'])

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
        edd_df = pd.read_csv(arquivo_edd, delimiter=';', encoding='utf-8')

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

# --- Execução do Script ---
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    passo3_dir = os.path.join(script_dir, "output", "passo3")
    passo4_dir = os.path.join(script_dir, "output", "passo4")
    os.makedirs(passo4_dir, exist_ok=True)

    arquivos_passo3 = glob.glob(os.path.join(passo3_dir, "*.csv"))
    if not arquivos_passo3:
        raise FileNotFoundError(f"Nenhum arquivo encontrado em: {passo3_dir}")
    arquivo_edd_match = max(arquivos_passo3, key=os.path.getmtime)

    for nome in ["noc_gpc_acesso.CSV", "noc_gpc_acesso.csv"]:
        caminho = os.path.join(script_dir, nome)
        if os.path.exists(caminho):
            arquivo_noc = caminho
            break
    else:
        raise FileNotFoundError(f"Arquivo 'noc_gpc_acesso.CSV' não encontrado em: {script_dir}")

    arquivo_saida = os.path.join(passo4_dir, "planta_ativa_edd_comparado.csv")

    print(f"Passo3:  {arquivo_edd_match}")
    print(f"Planta:  {arquivo_noc}")

    try:
        edd_df = pd.read_csv(arquivo_edd_match, delimiter=';', encoding='utf-8', low_memory=False)
        noc_df = pd.read_csv(arquivo_noc, sep=None, engine='python', encoding='latin-1', on_bad_lines='warn')

        edd_df['chave'] = edd_df['DESIGNACAO_ACESSO'].astype(str).str.lower().str.strip()
        noc_df['chave_noc'] = noc_df['nome_eqpto'].astype(str).str.lower().str.strip()
        ips_noc = set(noc_df['ip_x'].astype(str).str.strip())

        resultado_df = pd.merge(
            edd_df,
            noc_df[['chave_noc']].drop_duplicates(),
            left_on='chave',
            right_on='chave_noc',
            how='left'
        )

        match_por_nome = resultado_df['chave_noc'].notna()
        match_por_ip = resultado_df['IP_EDD'].astype(str).str.strip().isin(ips_noc)
        resultado_df['Presente_Planta'] = (match_por_nome | match_por_ip).map({True: 'ENCONTRADO', False: 'Não encontrado'})
        resultado_df = resultado_df.drop(columns=['chave', 'chave_noc'])

        resultado_df.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8-sig')

        total = len(resultado_df)
        encontrados = (resultado_df['Presente_Planta'] == 'ENCONTRADO').sum()
        print(f"\nConcluído! Arquivo salvo em: {arquivo_saida}")
        print(f"  Total de registros: {total}")
        print(f"  Presentes na planta: {encontrados}")
        print(f"  Não encontrados:     {total - encontrados}")

    except KeyError as e:
        print(f"Erro: Coluna {e} não encontrada em um dos arquivos.")
    except Exception as e:
        print(f"Erro inesperado: {e}")