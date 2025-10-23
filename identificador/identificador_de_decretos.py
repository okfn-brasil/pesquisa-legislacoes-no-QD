import os
import re
import pandas as pd

# Caminho base do projeto (sobe um nível da pasta identificador/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Leis analisadas
LEIS = ["LAI", "LGD", "LGPD", "MROSC"]

# Quantos caracteres ao redor do decreto extrair do texto
TRECHO_LIMITE = 300


def ler_txts():
    """Lê todos os arquivos .txt nas pastas dados_extraidos e retorna um dicionário {nome_arquivo_sem_ext: {...}}"""
    textos = {}

    for lei in LEIS:
        for tipo in ["capital", "estado"]:
            pasta_txt = os.path.join(BASE_DIR, lei, tipo, "dados_extraidos")
            if not os.path.exists(pasta_txt):
                continue

            for arquivo in os.listdir(pasta_txt):
                if arquivo.lower().endswith(".txt"):
                    caminho_txt = os.path.join(pasta_txt, arquivo)
                    try:
                        with open(caminho_txt, "r", encoding="utf-8") as f:
                            conteudo = f.read()
                    except UnicodeDecodeError:
                        with open(caminho_txt, "r", encoding="latin-1") as f:
                            conteudo = f.read()

                    chave = os.path.splitext(arquivo)[0]
                    textos[chave] = {"caminho": caminho_txt, "conteudo": conteudo}

    print(f"📄 Total de arquivos .txt carregados: {len(textos)}")
    return textos


def buscar_trecho(texto, termo):
    """Procura o termo no texto e retorna um trecho contextual começando em 'decreto' se encontrado."""
    if not termo or not isinstance(texto, str):
        return None

    termo_limpo = re.escape(str(termo).strip())
    padrao = re.compile(termo_limpo, flags=re.IGNORECASE)
    match = padrao.search(texto)
    
    if match:
        # Procurar a palavra "decreto" antes do termo
        trecho_antes = texto[:match.start()]
        padrao_decreto = re.compile(r'\bdecreto\b', flags=re.IGNORECASE)
        matches_decreto = list(padrao_decreto.finditer(trecho_antes))
        
        if matches_decreto:
            # Pega o último "decreto" antes do termo
            start = matches_decreto[-1].start()
        else:
            # Se não encontrar "decreto", mantém o comportamento anterior
            start = max(0, match.start() - TRECHO_LIMITE // 2)
        
        end = min(len(texto), match.end() + TRECHO_LIMITE // 2)
        return texto[start:end].strip()
    
    return None

def carregar_csvs_identificados():
    """Carrega todos os identificado_<LEI>.csv que existirem e retorna dict {LEI: df}"""
    pasta_identificados = os.path.join(BASE_DIR, "identificador", "identificado")
    csvs = {}
    for lei in LEIS:
        caminho_csv = os.path.join(pasta_identificados, f"identificado_{lei}.csv")
        if os.path.exists(caminho_csv):
            try:
                df = pd.read_csv(caminho_csv, encoding="utf-8", dtype=str)
            except UnicodeDecodeError:
                df = pd.read_csv(caminho_csv, encoding="latin-1", dtype=str)
            csvs[lei] = df.fillna("")
            print(f"✅ CSV carregado: identificado_{lei}.csv → {len(df)} linhas")
        else:
            print(f"[IGNORADO] CSV não encontrado: identificado_{lei}.csv")
    return csvs


def identificar_por_arquivo(textos, csvs):
    """Procura decretos e retorna apenas os casos com match"""
    pasta_saida = os.path.join(BASE_DIR, "identificador", "resultados")
    os.makedirs(pasta_saida, exist_ok=True)

    resultados_por_lei = {lei: [] for lei in LEIS}

    for nome_arquivo, info in textos.items():
        nome_arquivo_upper = nome_arquivo.upper()
        conteudo = info["conteudo"]

        lei_encontrada = next((lei for lei in LEIS if lei in nome_arquivo_upper), None)
        if not lei_encontrada:
            continue

        if lei_encontrada not in csvs:
            continue

        df = csvs[lei_encontrada]

        # Detecta colunas relevantes
        col_num_original = next((c for c in df.columns if "(original)" in c.lower()), None)
        col_num_extraido = next((c for c in df.columns if "número extraído" in c.lower() or "numero extraido" in c.lower()), None)
        col_nome = next((c for c in df.columns if c.lower().strip() == "nome"), None)
        col_capital_estado = next((c for c in df.columns if "capital" in c.lower() and "estado" in c.lower()), None)

        for _, row in df.iterrows():
            municipio = str(row.get(col_nome, "")).strip() if col_nome else ""
            valor_original = str(row.get(col_num_original, "")).strip() if col_num_original else ""
            valor_extraido = str(row.get(col_num_extraido, "")).strip() if col_num_extraido else ""
            capital_estado = str(row.get(col_capital_estado, "")).strip() if col_capital_estado else ""

            trecho = buscar_trecho(conteudo, valor_original) if valor_original else None
            if not trecho and valor_extraido:
                trecho = buscar_trecho(conteudo, valor_extraido)

            # 🔹 Somente adiciona se encontrou match
            if trecho:
                resultados_por_lei[lei_encontrada].append({
                    "Arquivo TXT": nome_arquivo,
                    "Caminho TXT": info["caminho"],
                    "Capital / Estado": capital_estado,
                    "Município (CSV)": municipio,
                    "Decreto (original)": valor_original,
                    "Decreto (número extraído)": valor_extraido,
                    "Trecho Encontrado": trecho
                })

        print(f"🔍 Processado: {nome_arquivo} → {lei_encontrada}")

    # 🔹 Salva apenas se houver matches
    for lei, resultados in resultados_por_lei.items():
        if resultados:
            df_res = pd.DataFrame(resultados)
            saida_csv = os.path.join(pasta_saida, f"decretos_identificados_por_arquivo_{lei}.csv")
            df_res.to_csv(saida_csv, index=False, encoding="utf-8-sig")
            print(f"✅ {lei}: {len(df_res)} decretos encontrados e salvos em {saida_csv}")
        else:
            print(f"[AVISO] Nenhum match encontrado para {lei}.")


def main():
    print("🚀 Iniciando identificador de decretos pelos nomes dos arquivos .txt...\n")
    textos = ler_txts()
    csvs = carregar_csvs_identificados()
    identificar_por_arquivo(textos, csvs)
    print("\n🏁 Processo finalizado.")


if __name__ == "__main__":
    main()
