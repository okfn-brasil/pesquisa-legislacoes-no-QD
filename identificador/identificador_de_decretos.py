import os
import re
import pandas as pd
import spacy
from spacy.matcher import Matcher

# Inicializa o modelo NLP e o matcher
nlp = spacy.load("pt_core_news_sm")
matcher = Matcher(nlp.vocab)

# Caminho base do projeto (sobe um nível da pasta identificador/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Leis analisadas
LEIS = ["LAI", "LGD", "LGPD", "MROSC"]

# Quantos caracteres ao redor do decreto extrair do texto
TRECHO_LIMITE = 300


# -------------------------------------------------------------------
# Lê todos os .txt disponíveis
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# Carrega os CSVs identificados
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# Função principal de identificação dos decretos
# -------------------------------------------------------------------
def identificar_por_arquivo(textos, csvs):
    """Usa spaCy Matcher para localizar o trecho do decreto conforme número da regulamentação"""
    pasta_saida = os.path.join(BASE_DIR, "identificador", "resultados")
    os.makedirs(pasta_saida, exist_ok=True)

    resultados_por_lei = {}

    for lei, df in csvs.items():
        resultados = []
        print(f"\n🔎 Processando {lei}...")

        for _, row in df.iterrows():
            numero_regulamentacao = str(row.get("Se sim, número da regulamentação (original)", "")).strip()
            if not numero_regulamentacao:
                continue

            # Nome base do arquivo (buscando sem extensão)
            nome_cidade = str(row.get("Município", "")).strip()
            if not nome_cidade:
                continue

            # Tenta encontrar o arquivo .txt correspondente
            possiveis_chaves = [k for k in textos.keys() if nome_cidade.lower() in k.lower()]
            if not possiveis_chaves:
                continue

            chave_txt = possiveis_chaves[0]
            texto = textos[chave_txt]["conteudo"]

            # Cria padrão de busca (regex + NLP)
            padrao_regex = re.escape(numero_regulamentacao)
            match = re.search(padrao_regex, texto, flags=re.IGNORECASE)

            if match:
                start, end = match.span()
                trecho_inicio = max(0, start - TRECHO_LIMITE)
                trecho_fim = min(len(texto), end + TRECHO_LIMITE)
                trecho_extraido = texto[trecho_inicio:trecho_fim].replace("\n", " ").strip()

                resultados.append({
                    "Lei": lei,
                    "Municipio": nome_cidade,
                    "Numero_Regulamentacao": numero_regulamentacao,
                    "Trecho_Encontrado": trecho_extraido
                })

        resultados_por_lei[lei] = resultados

        # Salva os resultados de cada lei
        if resultados:
            df_res = pd.DataFrame(resultados)
            saida_csv = os.path.join(pasta_saida, f"decretos_identificados_{lei}.csv")
            df_res.to_csv(saida_csv, index=False, encoding="utf-8-sig")
            print(f"✅ {lei}: {len(df_res)} decretos encontrados e salvos em {saida_csv}")
        else:
            print(f"[AVISO] Nenhum match encontrado para {lei}.")

    return resultados_por_lei


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
def main():
    print("🚀 Iniciando identificador de decretos pelos nomes dos arquivos .txt...\n")
    textos = ler_txts()
    csvs = carregar_csvs_identificados()
    identificar_por_arquivo(textos, csvs)
    print("\n🏁 Processo finalizado.")


if __name__ == "__main__":
    main()
