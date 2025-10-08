# percorrer os diretorios até chegar nos subdiretório dados brutos existente em cada um
# para cada documento dentro de dados_brutos, evoca uma biblioteca para extrair

#for entry in os.scandir(directory):  # LAI, LGD, etc
    # se o nome do subdiretorio for dados_brutos
        # entra no diretório
            # para cada documento de dados_brutos:
                # if documento is pdf: extrai com pypdf -> txt
                # if documento is html: extrai com BS -> txt
                # if documento is txt: não precisa extração -> txt

                # fez a extração, guardou o txt em dados_extraidos

import os
import pymupdf

laws = ["LAI", "LGD", "LGPD", "MROSC"]
territory_types = ["capitais","estados"]
directory = os.getcwd()
dados_brutos_directory = "//dados_brutos"
dados_extraidos_directory = "//dados_extraidos"

for entry in os.scandir(directory):
    if(entry.name in laws):
        for subentry in os.scandir(entry):
            if(os.path.isdir(subentry) and subentry.name in territory_types):
                dados_brutos_full_path = subentry.path + "//" + dados_brutos_directory
                dados_extraidos_full_path = subentry.path + "//" + dados_extraidos_directory
                for file in os.scandir(subentry.path + "//" + dados_brutos_directory):
                    file_name, file_extension = os.path.splitext(file.name)
                    dados_extraidos_full_file_path = dados_extraidos_full_path + "//" + file_name + ".txt"
                    if os.path.exists(dados_extraidos_full_file_path):
                        print(file.name, "Extração do arquivo já realizada")
                    else:
                        match file_extension:
                            case ".txt":
                                print(file.name, "Arquivo bruto já está em txt, apenas copiando para a pasta dados_extraidos")
                            case ".pdf":
                                print(file.name, "Convertendo pdf para txt")
                                doc = pymupdf.open(file.path)
                                out = open(dados_extraidos_full_file_path, "wb") # create a text output
                                for page in doc:
                                    text = page.get_text().encode("utf8") 
                                    out.write(text) 
                                    out.write(bytes((12,)))
                                out.close()
                            case ".html":
                                print(file.name, "Convertendo html para txt")
                            case ".htm":
                                print(file.name, "Convertendo html para txt")
                            case _:
                                print(file.name, "Tipo de arquivo não identificado")
                                      