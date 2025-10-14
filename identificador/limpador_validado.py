import os
import re
import pandas as pd

# Caminho base (sobe um nível da pasta identificador/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pastas principais com leis
LEIS = ["LAI", "LGD", "LGPD", "MROSC"]

# Padrões de número de decreto
PADRAO_COM_PONTO = re.compile(r"\b\d{1,3}\.\d{3}\b")  # Ex: 35.606, 123.456
PADRAO_SIMPLES = re.compile(r"\b\d{3,6}\b")           # Ex: 1234, 35606, 123456


def eh_ano_plausivel(num_str: str) -> bool:
    """Retorna True se num_str for um ano entre 1900 e 2099."""
    try:
        valor = int(num_str)
        return 1900 <= valor <= 2099
    except ValueError:
        return False


def extrair_numero(texto):
    """
    Extrai o número do decreto:
      - Prioriza formato com ponto (ex: 35.606)
      - Caso não exista, pega número 3–6 dígitos que NÃO seja ano (1900–2099)
    """
    if texto is None:
        return None

    texto_str = str(texto).strip()
    if not texto_str or texto_str.lower() in ("nan", "none", "n/a", "-"):
        return None

    # 1️⃣ Padrão com ponto
    match = PADRAO_COM_PONTO.search(texto_str)
    if match:
        return match.group(0)

    # 2️⃣ Padrão simples (descartando anos)
    for m in PADRAO_SIMPLES.finditer(texto_str):
        candidato = m.group(0)
        if not eh_ano_plausivel(candidato):
            return candidato

    return None


def limpar_csv(caminho_csv, nome_lei):
    print(f"🧹 Limpando {caminho_csv} ...")

    try:
        df = pd.read_csv(caminho_csv, encoding='utf-8', dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin-1', dtype=str)

    df.columns = df.columns.str.strip()

    # Localiza colunas
    col_capital_estado = next((c for c in df.columns if "capital" in c.lower() or "estado" in c.lower()), None)
    col_nome = next((c for c in df.columns if c.lower().strip() == "nome"), None)
    col_regulamenta = next((c for c in df.columns if "regulamenta" in c.lower()), None)

    if not all([col_capital_estado, col_nome, col_regulamenta]):
        print(f"[AVISO] Colunas esperadas não encontradas completamente em {nome_lei}")
        print(f"Encontradas: {col_capital_estado}, {col_nome}, {col_regulamenta}")

    # Filtra colunas válidas
    df_limpo = df[[c for c in [col_capital_estado, col_nome, col_regulamenta] if c is not None]].copy()

    # Renomeia para padrão fixo
    mapa_renomear = {
        col_capital_estado: "Capital / Estado",
        col_nome: "Nome",
        col_regulamenta: "Decreto"
    }
    df_limpo.rename(columns=mapa_renomear, inplace=True)

    # Extrai apenas o número do decreto
    if "Decreto" in df_limpo.columns:
        df_limpo["Decreto"] = df_limpo["Decreto"].apply(extrair_numero)

    # Cria pasta de saída
    pasta_saida = os.path.join(BASE_DIR, "identificador", "identificado")
    os.makedirs(pasta_saida, exist_ok=True)

    # Caminho final
    saida_csv = os.path.join(pasta_saida, f"identificado_{nome_lei}.csv")
    df_limpo.to_csv(saida_csv, index=False, encoding='utf-8-sig')

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
