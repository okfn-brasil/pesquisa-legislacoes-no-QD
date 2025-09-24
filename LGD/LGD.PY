# %%
CAPITAIS = {
    2800308: "Aracaju (SE)",
    3106200: "Belo Horizonte (MG)",
    1501402: "Belém (PA)",
    1400100: "Boa Vista (RR)",
    5002704: "Campo Grande (MS)",
    5300108: "Brasília (DF)",
    5103403: "Cuiabá (MT)",
    4106902: "Curitiba (PR)",
    5208707: "Goiânia (GO)",
    4205407: "Florianópolis (SC)",
    2507507: "João Pessoa (PB)",
    1600303: "Macapá (AP)",
    2704302: "Maceió (AL)",
    1302603: "Manaus (AM)",
    2408102: "Natal (RN)",
    1721000: "Palmas (TO)",
    4314902: "Porto Alegre (RS)",
    2611606: "Recife (PE)",
    3304557: "Rio de Janeiro (RJ)",
    2927408: "Salvador (BA)",
    2111300: "São Luís (MA)",
    2211001: "Teresina (PI)",
    3205309: "Vitória (ES)"
}

# %%
import requests


# %%
# URL base da API do Querido Diário para a consulta de diários oficiais
API_BASE_URL = "https://queridodiario.ok.org.br/api/gazettes"

# OPÇÕES DE PESQUISA
distancia_max_entre_termos = 15
lista_de_palavras = ["Lei"]

opcoes_de_pesquisa = [
    {"numero": "14.129", "ano": 2021, "nome": "Lei Governo Digital", "sigla":"LGD"},
]

# TODO: avaliar futuramente se "lei" não seria uma stopword dentro do contexto


# %%
def verifica_regulamentacao(cidade_id, query_lei):

    params = {
        "querystring": query_lei,
        "territory_ids": cidade_id,
        "published_since": '2021-07-20',
        "excerpt_size": 2000
    }

    response = requests.get(API_BASE_URL, params=params)
    dados = response.json()
    return dados.get("total_gazettes")

# %%
print("Iniciando a verificação de regulamentação de leis nas capitais...")
resultados_finais = {nome_cidade: {} for nome_cidade in CAPITAIS.values()}

for lei_a_ser_buscada in opcoes_de_pesquisa:
    
    pesquisa_completa = ""
    # Esta linha foi modificada para garantir que a pesquisa_completa seja construída corretamente
    for palavra_chave in lista_de_palavras:
        texto_bruto = f'"{palavra_chave} {lei_a_ser_buscada["numero"]}"~{distancia_max_entre_termos}'
        texto_bruto_sem_ponto = texto_bruto.replace(".", "")
        pesquisa_completa += f"{texto_bruto} {texto_bruto_sem_ponto} "
    
    for cidade_id, nome_cidade in CAPITAIS.items():
        qnt_de_resultados = verifica_regulamentacao(cidade_id, pesquisa_completa)
        
        # Armazena os resultados no dicionário
        resultados_finais[nome_cidade][lei_a_ser_buscada['sigla']] = qnt_de_resultados
        
        print(f"{nome_cidade} | {lei_a_ser_buscada['sigla']} | Qnt resultados: {qnt_de_resultados}")

