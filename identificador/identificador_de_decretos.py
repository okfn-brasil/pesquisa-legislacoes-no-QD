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
    """
    Lê todos os arquivos .txt nas pastas dados_extraidos e retorna um dicionário
    {nome_arquivo_sem_ext: {"caminho": ..., "conteudo": ...}}
    """
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

                    chave = os.path.splitext(arquivo)[0]  # mantemos case original do nome do arquivo (sem extensão)
                    textos[chave] = {"caminho": caminho_txt, "conteudo": conteudo}

    print(f"📄 Total de arquivos .txt carregados: {len(textos)}")
    return textos


def buscar_trecho(texto, termo):
    """Procura o termo no texto e retorna um trecho contextual se encontrado."""
    if not termo or not isinstance(texto, str):
        return None

    termo_limpo = re.escape(str(termo).strip())
    padrao = re.compile(termo_limpo, flags=re.IGNORECASE)
    match = padrao.search(texto)
    if match:
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
            csvs[lei] = df.fillna("")  # evita NaN
            print(f"✅ CSV carregado: identificado_{lei}.csv → {len(df)} linhas")
        else:
            print(f"[IGNORADO] CSV não encontrado: identificado_{lei}.csv")
    return csvs


def identificar_por_arquivo(textos, csvs):
    """
    Para cada arquivo .txt, detecta a LEI pelo nome do arquivo e procura os valores das colunas
    'Se sim, número da regulamentação (original)' (primeiro) e depois '(número extraído)' no texto.
    Gera um CSV de resultados por LEI.
    """
    pasta_saida = os.path.join(BASE_DIR, "identificador", "resultados")
    os.makedirs(pasta_saida, exist_ok=True)

    # agrupar resultados por lei
    resultados_por_lei = {lei: [] for lei in LEIS}

    for nome_arquivo, info in textos.items():
        nome_arquivo_upper = nome_arquivo.upper()
        conteudo = info["conteudo"]

        # detectar qual LEI pertence ao arquivo pelo próprio nome do arquivo
        lei_encontrada = None
        for lei in LEIS:
            if lei in nome_arquivo_upper:
                lei_encontrada = lei
                break

        if not lei_encontrada:
            # pula arquivos que não mencionam nenhuma das LEIS no nome
            print(f"[PULAR] '{nome_arquivo}' - nenhuma das LEIS encontrada no nome do arquivo.")
            continue

        # checar se temos o CSV carregado para essa lei
        if lei_encontrada not in csvs:
            print(f"[PULAR] '{nome_arquivo}' - CSV identificado_{lei_encontrada}.csv não carregado.")
            continue

        df = csvs[lei_encontrada]

        # tentaremos buscar cada linha do CSV dentro deste arquivo .txt
        # (pode gerar vários matches por arquivo, se o CSV tiver múltiplos municípios que correspondam)
        for _, row in df.iterrows():
            # identifica colunas com possíveis nomes (insensível a caixa)
            # prioridade: "(original)" depois "(número extraído)"
            col_num_original = next((c for c in df.columns if "(original)" in c.lower()), None)
            col_num_extraido = next((c for c in df.columns if "número extraído" in c.lower() or "numero extraido" in c.lower()), None)
            col_nome = next((c for c in df.columns if c.lower().strip() == "nome"), None)

            municipio = str(row.get(col_nome, "")).strip() if col_nome else ""
            valor_original = str(row.get(col_num_original, "")).strip() if col_num_original else ""
            valor_extraido = str(row.get(col_num_extraido, "")).strip() if col_num_extraido else ""

            # 1) tenta buscar pelo valor original (exato)
            trecho = None
            if valor_original:
                trecho = buscar_trecho(conteudo, valor_original)

            # 2) se não encontrou, tenta com o número extraído
            if not trecho and valor_extraido:
                trecho = buscar_trecho(conteudo, valor_extraido)

            # se não encontrou nada, marca como não encontrado
            if not trecho:
                trecho = "❌ Decreto não encontrado no texto"

            resultados_por_lei[lei_encontrada].append({
                "Arquivo TXT": nome_arquivo,
                "Caminho TXT": info["caminho"],
                "Município (CSV)": municipio,
                "Decreto (original)": valor_original,
                "Decreto (número extraído)": valor_extraido,
                "Trecho Encontrado": trecho
            })

        print(f"🔎 Processado: {nome_arquivo}  → {lei_encontrada} (verificadas {len(df)} linhas do CSV)")

    # salvar resultados por lei
    for lei, resultados in resultados_por_lei.items():
        if not resultados:
            print(f"[AVISO] Nenhum resultado para {lei}, pulando gravação.")
            continue
        df_res = pd.DataFrame(resultados)
        saida_csv = os.path.join(pasta_saida, f"decretos_identificados_por_arquivo_{lei}.csv")
        df_res.to_csv(saida_csv, index=False, encoding="utf-8-sig")
        print(f"✅ Resultados salvos: {saida_csv} ({len(df_res)} registros)")


def main():
    print("🚀 Iniciando identificador de decretos pelos nomes dos arquivos .txt...\n")
    textos = ler_txts()
    csvs = carregar_csvs_identificados()
    identificar_por_arquivo(textos, csvs)
    print("\n🏁 Processo finalizado.")


if __name__ == "__main__":
    main()
