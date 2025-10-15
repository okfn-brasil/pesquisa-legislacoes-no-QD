import os
import re
import pandas as pd

# Caminho base (sobe um nível da pasta identificador/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pastas principais com leis
LEIS = ["LAI", "LGD", "LGPD", "MROSC"]

def limpar_csv(caminho_csv, nome_lei):
    print(f"🧹 Limpando {caminho_csv} ...")

    # 1) Lê CSV
    try:
        df = pd.read_csv(caminho_csv, encoding='utf-8', dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin-1', dtype=str)

    df.columns = df.columns.str.strip()

    # 2) Identifica colunas principais
    col_capital_estado = next((c for c in df.columns if "capital" in c.lower() or "estado" in c.lower()), None)
    col_nome = next((c for c in df.columns if c.lower().strip() == "nome"), None)

    # 🔍 Coluna “Encontrou regulamentação”
    col_encontrou = next((c for c in df.columns if c.lower().startswith("encontrou regulamentação")), None)

    # 🔗 Coluna do número da regulamentação
    col_regulamenta = "Se sim, número da regulamentação" if "Se sim, número da regulamentação" in df.columns else None

    # 3) Verifica se as colunas principais foram encontradas
    if not col_regulamenta:
        print(f"[AVISO] Coluna de regulamentação não encontrada em {nome_lei}")

    if not all([col_capital_estado, col_nome, col_encontrou]):
        print(f"[AVISO] Colunas principais ausentes em {nome_lei}")
        print(f"Encontradas: {col_capital_estado}, {col_nome}, {col_encontrou}")

    # 4) Define colunas válidas (mantém a ordem lógica e remove link)
    colunas_validas = [c for c in [col_capital_estado, col_nome, col_encontrou, col_regulamenta] if c is not None]
    df = df[colunas_validas].copy()

    # 5) Filtra linhas com base nos critérios de regulamentação
    if col_encontrou:
        df = df[df[col_encontrou].astype(str).str.strip().str.lower() == "sim"]

    if col_regulamenta:
        df = df[df[col_regulamenta].notna() & (df[col_regulamenta].str.strip() != "")]

    # 5.1) 🧩 Cria coluna com número extraído e mantém a original
    if col_regulamenta in df.columns:

        # Renomeia a original
        df.rename(columns={col_regulamenta: f"{col_regulamenta} (original)"}, inplace=True)

        # Regex melhorada:
        pattern = re.compile(
            r'\b(?!19\d{2}\b|20\d{2}\b)(\d{1,2}(?:\.\d{3})+|\d{3,5})(?=[^\d]|$)',
            flags=re.IGNORECASE
        )

        def extrair_decreto(texto):
            if pd.isna(texto):
                return None
            texto_str = str(texto)
            # remove datas do tipo “de 2024”
            texto_str = re.sub(r'\bde\s+(19|20)\d{2}\b', '', texto_str, flags=re.IGNORECASE)
            match = pattern.search(texto_str)
            if match:
                return match.group(1)
            alt = re.search(r'\b(?!19\d{2}\b|20\d{2}\b)\d{3,5}\b', texto_str)
            return alt.group(0) if alt else texto_str.strip()

        # Cria a nova coluna apenas com o número
        df[f"{col_regulamenta} (número extraído)"] = df[f"{col_regulamenta} (original)"].astype(str).apply(extrair_decreto)

    # 6) Cria pasta de saída e salva CSV
    pasta_saida = os.path.join(BASE_DIR, "identificador", "identificado")
    os.makedirs(pasta_saida, exist_ok=True)
    saida_csv = os.path.join(pasta_saida, f"identificado_{nome_lei}.csv")
    df.to_csv(saida_csv, index=False, encoding='utf-8-sig')

    print(f"✅ Arquivo salvo em: {saida_csv}\n")


def main():
    print("🚀 Iniciando limpeza dos arquivos validado_*.csv\n")
    for lei in LEIS:
        caminho_csv = os.path.join(BASE_DIR, lei, f"validado_{lei}.csv")
        if os.path.exists(caminho_csv):
            limpar_csv(caminho_csv, lei)
        else:
            print(f"[IGNORADO] Arquivo não encontrado: {caminho_csv}")
    print("🏁 Processo concluído!")


if __name__ == "__main__":
    main()
