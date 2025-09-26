import os
import requests
import pandas as pd
from datetime import datetime, timedelta

API_BASE_URL = "https://queridodiario.ok.org.br/api/gazettes"
EXCERPT_SIZE = 2000

CAPITAIS = {
    "Aracaju (SE)": 2800308,
    "Belo Horizonte (MG)": 3106200,
    "Belém (PA)": 1501402,
    "Boa Vista (RR)": 1400100,
    "Campo Grande (MS)": 5002704,
    "Brasília (DF)": 5300108,
    "Cuiabá (MT)": 5103403,
    "Curitiba (PR)": 4106902,
    "Goiânia (GO)": 5208707,
    "Florianópolis (SC)": 4205407,
    "João Pessoa (PB)": 2507507,
    "Macapá (AP)": 1600303,
    "Maceió (AL)": 2704302,
    "Manaus (AM)": 1302603,
    "Natal (RN)": 2408102,
    "Palmas (TO)": 1721000,
    "Porto Alegre (RS)": 4314902,
    "Recife (PE)": 2611606,
    "Rio de Janeiro (RJ)": 3304557,
    "Salvador (BA)": 2927408,
    "São Luís (MA)": 2111300,
    "Teresina (PI)": 2211001,
    "Vitória (ES)": 3205309
}

CSV_FILE_PATH = "MROSC.csv"
MROSC_NUMBER = "13.019"
DATE_FORMAT = "%d/%m/%Y"
DATE_SEARCH_FORMAT = "%Y-%m-%d"
EXCERPT_SIZE = 2000
DAYS_TO_ADD_START = 0
DAYS_TO_ADD_END = 14
DOWNLOAD_PDF = False

try:
    df = pd.read_csv(
        CSV_FILE_PATH,
        sep=";",
        dtype={"Número": str},
        keep_default_na=False
    )
    #print(df.head())
    #print(df.dtypes)

    for index, row in df.iterrows():
        numero = str(row["Número"]).strip()
        #print(row)
        if numero:
            querystring = MROSC_NUMBER + "+" + row["Número"]
            territory_id = CAPITAIS[row["Município (UF)"]]
            # uma suave gambiarra para não ter que lidar com datas...
            published_since = "2014-01-01"
            published_until = "2025-01-01"

            """
            try:           
                publish_date = datetime.strptime(row["Data"], DATE_FORMAT).date()
                start_time_delta = timedelta(days=DAYS_TO_ADD_START)
                published_since_date = publish_date + start_time_delta 
                published_since = published_since_date.strftime(DATE_SEARCH_FORMAT)
                end_time_delta = timedelta(days=DAYS_TO_ADD_END)
                published_until_date = published_since_date + end_time_delta
                published_until = published_until_date.strftime(DATE_SEARCH_FORMAT)
            except Exception:
                published_since = row["Data"] + "-01-01"
                published_until = str(int(row["Data"])+1) + "-01-01" 
            """
      
       
            params = {
                "querystring": querystring,
                "territory_ids": territory_id,
                "published_since": published_since,
                "published_until": published_until,
                "excerpt_size": 2000
            }
            
            response = requests.get(API_BASE_URL, params=params)
            dados = response.json()
            #print("debug")
            print(row["Município (UF)"], dados.get("total_gazettes"))
            #print(dados)
            if dados.get("total_gazettes") > 0:
                territory_folder_path = row["Município (UF)"]
                os.makedirs(territory_folder_path, exist_ok=True)
                excerpts = dados.get("excerpts") 
                for gazette in dados.get("gazettes"):
                    file_content = gazette["excerpts"][0]
                    file_name = row["Município (UF)"] + "/" + gazette["date"] + ".txt"
                    with open(file_name, "w", encoding='utf-8') as f:
                        f.write(file_content)
                    response_gazette_file = requests.get(gazette["txt_url"], stream=True)
                    response_gazette_file.raise_for_status()
                    gazzete_base_file_name = row["Município (UF)"] + "/" + gazette["date"] + "_full_gazzete"
                    gazette_file_name = gazzete_base_file_name + "txt"
                    with open(gazette_file_name, "wb") as f:
                        for chunk in response_gazette_file.iter_content(chunk_size=8192):
                            f.write(chunk)
                    if DOWNLOAD_PDF:
                        response_gazette_pdf_file = requests.get(gazette["url"])
                        with open(gazzete_base_file_name + ".pdf", "wb") as pdf_file:
                            pdf_file.write(response_gazette_pdf_file.content)
                
except Exception as e:
    print("ERRO")
    print(e)                

      
