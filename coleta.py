
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

laws = ["LGD", "LGPD", "MROSC"]
territory_types = ["capitais","estados"]
directory = os.getcwd()

dados_brutos_directory = "//dados_brutos"
dados_extraidos_directory = "//dados_extraidos"

import csv
import requests
from unidecode import unidecode

for entry in os.scandir(directory):
    if(entry.name in laws):
        for local_file in os.scandir(entry):
            file_name, file_extension = os.path.splitext(local_file.name)
            if file_extension == ".csv":
                with open(local_file, mode ='r') as file:
                    csvFile = csv.DictReader(file)
                    for lines in csvFile:
                        file_source = lines['Se sim, link da regulamentação']
                        
                        if ".pdf" in file_source:
                            extension = "pdf"
                        elif ".html" in file_source:
                            extension = "html"
                        else:
                            breakpoint()

                        download_directory = f'./{entry.name}/{lines["Capital / Estado"].lower()}/dados_brutos'
                        output_file = f"{unidecode(lines['Nome'].split()[0])}_{entry.name}.{extension}"
                        full_save_path = os.path.join(download_directory, output_file)

                        try:
                            response = requests.get(file_source, stream=True)
                            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                            with open(full_save_path, 'wb') as save_file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    save_file.write(chunk)
                            print(f"File downloaded successfully to: {full_save_path}")

                        except requests.exceptions.RequestException as e:
                            print(f"Error downloading PDF: {e}")
                        except IOError as e:
                            print(f"Error saving PDF file: {e}")

                        


                        

                        

