
# # https://www.geeksforgeeks.org/python/how-to-iterate-over-files-in-directory-using-python/

# import os  # import os module

# directory = 'files'  # set directory path

# for entry in os.scandir(directory):  # LAI, LGD, etc
#     if not entry.is_file():  # LAI
#         for entry in os.scandir(directory): #dados_brutos, LAI.csv, validado_LAI.csv
#             # open(validado_LAI.csv)
#             # iteração na tabela aberta, a coluna "Se sim, link da regulamentação",
#             # requisitando os links, por exemplo com requests
#             # obtido o doc para rio branco, salvar o doc em LAI/dados_brutos
#             # UF_nome_SIGLA-DA-LEI.pdf

import os
import time
import logging

import csv
import requests
from urllib.parse import urlparse
from unidecode import unidecode


# Configuração básica do logger
logging.basicConfig(
    level=logging.INFO,  # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("download_regulamentacoes.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Cria uma session para evitar tantos problemas de download...
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml; q=0.9, */*; q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
})

laws = ["LGD", "LGPD", "MROSC"]
territory_types = ["capitais","estados"]
directory = os.getcwd()

dados_brutos_directory = "//dados_brutos"
dados_extraidos_directory = "//dados_extraidos"


for entry in os.scandir(directory):
    if entry.name in laws and entry.is_dir():
        for local_file in os.scandir(entry):
            file_name, file_extension = os.path.splitext(local_file.name)
            if file_extension == ".csv":
                with open(local_file.path, mode ='r') as file:
                    csvFile = csv.DictReader(file)
                    for lines in csvFile:
                        
                        # --- detectar dinamicamente a coluna de Sim ou Não ---
                        coluna_encontrou = None
                        for key in lines.keys():
                            # normaliza acentuação e maiúsculas para comparação robusta
                            if "encontrou regulamentacao" in unidecode(key).lower():
                                coluna_encontrou = key
                                break

                        # obtém o valor (sim/não) e só prossegue se contiver "sim"
                        resposta = (lines.get(coluna_encontrou) or "").strip().lower()
                        if not resposta.startswith("sim"):
                            continue

                        # agora sim, processa o link
                        file_source = (lines.get('Se sim, link da regulamentação') or '').strip()
                        #print(file_source)
                        
                        download_directory = f'./{entry.name}/{lines["Capital / Estado"].lower()}/dados_brutos'

                        try:
                            # colocando headers para não ficarem pistola...
                            parsed = urlparse(file_source)
                            origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else None
                            req_headers = {}
                            if origin:
                                #req_headers["Referer"] = origin
                                session.get(origin, timeout=(5, 15))
                                time.sleep(4)

                            time.sleep(4) # soneca básica para não sobrecarregar...
                            response = session.get(
                                file_source,
                                headers=req_headers,
                                stream=True,
                                timeout=(5, 60),
                                allow_redirects=True,
                            )
                            response.raise_for_status()

                            #response = requests.get(file_source, stream=True, timeout=(5, 60))
                            #response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                            # decidndo qual extensão usar
                            # usa a URL final pós-redirecionamento (response.url)
                            final_url = (response.url or file_source).lower()
                            if final_url.endswith(".pdf"):
                                extension = "pdf"
                            elif final_url.endswith((".html", ".htm")):
                                extension = "html"
                            else:
                                # Usando o Content-Type como evidência
                                ct = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                                if ct == "application/pdf":
                                    extension = "pdf"
                                elif ct in ("text/html", "application/xhtml+xml"):
                                    extension = "html"
                                else:
                                    # Se der ruim...
                                    extension = "bin"

                            output_file = f"{unidecode(lines['Nome'].split()[0])}_{entry.name}.{extension}"
                            full_save_path = os.path.join(download_directory, output_file)
                            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)


                            with open(full_save_path, 'wb') as save_file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    save_file.write(chunk)
                            logging.info(f" - OK Downloaded to: {full_save_path}")

                        #except requests.exceptions.RequestException as e:
                        #    print(f"Error downloading PDF: {e}")
                        #except IOError as e:
                        #    print(f"Error saving PDF file: {e}")

                        
                        except requests.exceptions.RequestException as e:
                            logging.error(f" - NETWORK Error downloading PDF: {e}")

                        except IOError as e:
                            logging.error(f" - WRITE Error saving PDF file: {e}")

                        except Exception as e:
                            logging.exception(f" - UKNOWN ERROR {e}")

                        

                        

