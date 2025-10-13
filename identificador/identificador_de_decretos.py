import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def extrair_numero_decreto(texto: str):
    """
    Extrai o número do decreto no formato 12.345, 35.606 etc.
    Retorna None se não encontrar.
    """
    if pd.isna(texto):
        return None
    match = re.search(r"\b\d{1,3}\.\d{3}\b", str(texto))
    return match.group(0) if match else None


def carregar_dados(lei: str):
    resultados = []

    lei_dir = os.path.join(BASE_DIR, lei)
    csv_path = os.path.join(lei_dir, f"validado_{lei}.csv")

    if not os.path.exists(csv_path):
        print(f"[AVISO] CSV não encontrado: {csv_path}")
        return pd.DataFrame()

    decretos_df = pd.read_csv(csv_path, encoding='utf-8', sep=',', dtype=str)
    decretos_df.columns = decretos_df.columns.str.strip()

    # Tenta encontrar a coluna com o número da regulamentação
    col_num = None
    for col in decretos_df.columns:
        if "regulamenta" in col.lower():
            col_num = col
            break

    if col_num is None:
        print(f"[ERRO] Coluna com número de regulamentação não encontrada em {csv_path}")
        return pd.DataFrame()

    # Extrai o número do decreto usando regex
    decretos_df["numero_decreto"] = decretos_df[col_num].apply(extrair_numero_decreto)

    # Tenta identificar a coluna do município (ou cidade)
    col_mun = None
    for col in decretos_df.columns:
        if "munic" in col.lower() or "cidade" in col.lower():
            col_mun = col
            break

    # Percorre capital e estado
    for nivel in ['capital', 'estado']:
        extrato_dir = os.path.join(lei_dir, nivel, 'dados_extraidos')
        if not os.path.exists(extrato_dir):
            continue

        for arquivo in os.listdir(extrato_dir):
            if arquivo.endswith(".txt"):
                caminho_txt = os.path.join(extrato_dir, arquivo)
                cidade = arquivo.split("_")[0]  # ex: "Macapa_LAI.txt" -> "Macapa"
                texto = open(caminho_txt, 'r', encoding='utf-8').read()

                # tenta achar o decreto da cidade no csv
                numero_decreto = None
                for _, row in decretos_df.iterrows():
                    nome_municipio = str(row.get(col_mun, '')).lower()
                    if cidade.lower() in nome_municipio:
                        numero_decreto = row.get('numero_decreto')
                        break

                resultados.append({
                    "tipo_lei": lei,
                    "nivel": nivel,
                    "nome_arquivo": arquivo,
                    "cidade": cidade,
                    "numero_decreto": numero_decreto,
                    "texto": texto
                })

    return pd.DataFrame(resultados)


def carregar_todas_as_leis():
    leis = ['LAI', 'LGD', 'LGPD', 'MROSC']
    dfs = [carregar_dados(lei) for lei in leis if os.path.exists(os.path.join(BASE_DIR, lei))]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


if __name__ == "__main__":
    df = carregar_todas_as_leis()
    print(f"Total de documentos carregados: {len(df)}")
    print(df.head())
