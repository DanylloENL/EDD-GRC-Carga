import pandas as pd
import os

input_dir = r'output\passo6'
output_base = r'output\passo7'
linhas_por_arquivo = 500

arquivos = ['centro', 'equipamento', 'interface']

for nome in arquivos:
    input_path = os.path.join(input_dir, f'{nome}.csv')
    output_dir = os.path.join(output_base, nome)
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(input_path, sep=';', dtype=str)
    df = df.drop_duplicates()

    for i, inicio in enumerate(range(0, len(df), linhas_por_arquivo), start=1):
        df_part = df.iloc[inicio:inicio + linhas_por_arquivo]
        df_part.to_csv(os.path.join(output_dir, f'{nome}_parte_{i}.csv'), sep=';', index=False)

    print(f'{nome}: {len(df)} linhas -> {i} arquivo(s)')

print("Divisão concluída!")
