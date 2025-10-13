import os
import re
import pandas as pd

# Caminho base (sobe um nível da pasta identificador/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEIS = ["LAI", "LGD", "LGPD", "MROSC"]

# Regex: captura o primeiro número com 3–6 dígitos, com ou sem ponto (ex: 12345, 35.606, 123.456)
PADRAO_DECRETO = re.compile(r"\b\d{3,6}(?:\.\d{1,3})?\b")

def extrair_numero(texto):
    """
    Extrai o primeiro número do decreto (3 a 6 dígitos, opcionalmente com ponto).
    Retorna None se não encontrar.
    """
    try:
        # Converte tudo para string simples
        texto_str = str(texto).strip()

        # Ignora valores vazios ou nulos
        if not texto_str or texto_str.lower() in ['nan', 'none']:
            return None

        # Aplica regex
        match = PADRAO_DECRETO.search(texto_str)
        return match.group(0) if match else None

    except Exception as e:
        print(f"[ERRO extrair_numero] Valor inesperado: {texto} ({e})")
        return None


def limpar_csv(caminho_csv, nome_lei):
    print(f"🧹 Limpando {caminho_csv} ...")

    try:
        df = pd.read_csv(caminho_csv, encoding='utf-8', dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin-1', dtype=str)

    # Normaliza nomes de colunas
    df.columns = df.columns.str.strip()

    # Localiza colunas desejadas
    colunas_desejadas = []
    for nome in df.columns:
        if "capital" in nome.lower() or "estado" in nome.lower():
            colunas_desejadas.append(nome)
        elif nome.lower() == "nome":
            colunas_desejadas.append(nome)
        elif "regulamenta" in nome.lower():
            colunas_desejadas.append(nome)

    # Aviso se não achou todas as colunas esperadas
    if len(colunas_desejadas) < 3:
        print(f"[AVISO] Nem todas as colunas esperadas foram encontradas em {nome_lei}")
        print(f"Colunas encontradas: {colunas_desejadas}")

    # Filtra e copia
    df_limpo = df[colunas_desejadas].copy()

    # Renomeia para padrão uniforme
    mapa_renomear = {
        c: "Capital / Estado" for c in colunas_desejadas if "capital" in c.lower() or "estado" in c.lower()
    }
    mapa_renomear.update({
        c: "Nome" for c in colunas_desejadas if c.lower() == "nome"
    })
    mapa_renomear.update({
        c: "Se sim, número da regulamentação" for c in colunas_desejadas if "regulamenta" in c.lower()
    })

    df_limpo.rename(columns=mapa_renomear, inplace=True)

    # Limpa a coluna do decreto
    if "Se sim, número da regulamentação" in df_limpo.columns:
        df_limpo["Se sim, número da regulamentação"] = df_limpo[
            "Se sim, número da regulamentação"
        ].astype(str).apply(extrair_numero)

    # Cria pasta de saída
    pasta_saida = os.path.join(BASE_DIR, "identificador", "identificado")
    os.makedirs(pasta_saida, exist_ok=True)

    # Caminho de saída
    saida_csv = os.path.join(pasta_saida, f"identificado_{nome_lei}.csv")
    df_limpo.to_csv(saida_csv, index=False, encoding='utf-8-sig')

    print(f"✅ Arquivo salvo em: {saida_csv}")


def main():
    for lei in LEIS:
        caminho_csv = os.path.join(BASE_DIR, lei, f"validado_{lei}.csv")
        if os.path.exists(caminho_csv):
            limpar_csv(caminho_csv, lei)
        else:
            print(f"[IGNORADO] Não encontrado: {caminho_csv}")


if __name__ == "__main__":
    main()
