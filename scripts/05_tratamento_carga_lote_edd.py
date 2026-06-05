import pandas as pd
import re

input_path = r'output\passo4\planta_ativa_edd_comparado.csv'
df = pd.read_csv(input_path, sep=';', encoding='utf-8', dtype=str)

# Filtrar linhas (Status_EDD = "Critical" ou "ENCONTRADO")
df = df[df["Status_EDD"].isin(["Critical", "ENCONTRADO"])]

# Excluir equipamentos já presentes na planta (cadastrados no sistema)
df = df[df["Presente_Planta"] != "ENCONTRADO"]

# Remover colunas que não são necessárias
remove_cols = ["PRODUTO", "RAZAO_SOCIAL", "TIPO_ACESSO", "STATUS"]
df = df.drop(columns=remove_cols, errors='ignore')

# Ajustar presente no NOC com base na coluna já existente, quando disponível
def map_presente_noc(valor):
    if pd.isna(valor):
        return "Não"
    valor = valor.strip().lower()
    if valor in ["encontrado", "encontrado", "encontrado no noc", "sim", "yes"]:
        return "Sim"
    if valor in ["não encontrado", "nao encontrado", "não", "nao", "não encontrado no noc", "não encontrado no noc"]:
        return "Não"
    return "Não"

if "Presente_NOC" in df.columns:
    df["PRESENTE_NOC_GPC"] = df["Presente_NOC"].apply(map_presente_noc)
else:
    df["PRESENTE_NOC_GPC"] = "Não"

# Criar "Sigla Centro" diretamente
filtro_sigla = df["DESIGNACAO_IP"].astype(str).str.split("/").str[0]
df["SIGLA_CENTRO"] = (filtro_sigla + "_" + df["DESIGNACAO_ACESSO"].astype(str).str.split("_").str[-1]).apply(lambda x: re.sub(r'[^A-Za-z0-9\-_]', '', x))

# Criar coluna "Equipamento" (cópia de DESIGNACAO_ACESSO em minúsculo, apenas chars válidos)
df["EQUIPAMENTO"] = df["DESIGNACAO_ACESSO"].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9\-\._]', '', x))

# Criar coluna "CNL" com o texto antes do delimitador "/"
df["CNL"] = filtro_sigla

# Reordenar colunas para a saída principal
df = df[[
    "PRESENTE_NOC_GPC", "DESIGNACAO_IP", "CNL", "DESIGNACAO_ACESSO",
    "Status_EDD", "IP_EDD", "SIGLA_CENTRO", "EQUIPAMENTO"
]]

# Renomear colunas
[df.rename(columns={
    "Status_EDD": "STATUS_EDD"
}, inplace=True)]

# Exibir resultado final
print(df.head())

# Salvar transformação intermediária
output_dir = r'output\passo6'
import os
os.makedirs(output_dir, exist_ok=True)

df.to_csv(os.path.join(output_dir, "saida_transformada.csv"), sep=';', encoding='utf-8', index=False)

# Gerar os três arquivos finais
# 1) Centro
centro = pd.DataFrame({
    "rede": "NOC GPC ACESSO",
    "cnl": df["CNL"],
    "sigla_centro": df["SIGLA_CENTRO"],
    "endereco": "AAA",
    "cep": "9999999",
    "contato": "CONTATO 1",
    "tipo_contato": "NORMAL",
    "telefone": "(21)99999-9999",
    "email": "contato@claro.com.br",
    "operadora": "CLARO",
    "tipo_centro": "SITE NORMAL",
    "dia_semana": "Dom,Seg,Ter,Qua,Qui,Sex,Sab",
    "horario_inicio": "00:00",
    "horario_fim": "23:59",
    "feriado": "N"
})
centro = centro.drop_duplicates(subset='sigla_centro')

# Filtrar apenas centros que ainda não existem no GRC
grc_centros = pd.read_csv(r'recursos\PORT_extrator_centro.csv', sep=';', dtype=str, encoding='latin-1', on_bad_lines='skip')
grc_siglas = set(grc_centros['sigla_centro'].astype(str).str.strip().str.upper())
centro = centro[~centro['sigla_centro'].str.strip().str.upper().isin(grc_siglas)]

print(f"Centros novos (não cadastrados no GRC): {len(centro)}")
centro.to_csv(os.path.join(output_dir, "centro.csv"), sep=';', index=False, encoding='utf-8')

# 2) Equipamento
equipamento = pd.DataFrame({
    "rede": "NOC GPC ACESSO",
    "sigla_centro": df["SIGLA_CENTRO"],
    "proprietario": "EMBRATEL",
    "modelo": "DM2104G2",
    "nome_eqpto": df["EQUIPAMENTO"],
    "ip": df["IP_EDD"],
    "controla_nat": "N",
    "eqpto_caract": "MPLS",
    "ipv6": "",
    "snmpver": "v2c",
    "num_serial": "",
    "protocolo_conexao": "telnet",
    "abre_pro_ativo": "S",
    "tipo_eqpto": "EDD",
    "dt_ativacao_tecnica": "05/09/2025"
})
equipamento.to_csv(os.path.join(output_dir, "equipamento.csv"), sep=';', index=False, encoding='utf-8')

# 3) Interface
interface = pd.DataFrame({
    "nome_rede": "NOC GPC ACESSO",
    "nome_eq": df["EQUIPAMENTO"],
    "ip_interface": "",
    "mascara_ip": "",
    "tipo_int": "CPE",
    "desig": "",
    "desig_acesso": df["DESIGNACAO_ACESSO"],
    "ifdescr": "Ethernet Port on unit 1, port:1",
    "tipo_funcao": "",
    "tecnologia": "Terrestre",
    "velocidade": "1000000000",
    "ip_v6": "",
    "ip_v6_mascara": "",
    "servico_rede": "ACESSO",
    "protocolo": "ETHERNET",
    "servico_gerencia": "IFOPERSTATUS",
    "dt_ativacao": "05/09/2025"
})
interface.to_csv(os.path.join(output_dir, "interface.csv"), sep=';', index=False, encoding='utf-8')
