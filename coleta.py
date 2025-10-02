
# https://www.geeksforgeeks.org/python/how-to-iterate-over-files-in-directory-using-python/

import os  # import os module

directory = 'files'  # set directory path

for entry in os.scandir(directory):  # LAI, LGD, etc
    if not entry.is_file():  # LAI
        for entry in os.scandir(directory): #dados_brutos, LAI.csv, validado_LAI.csv
            # open(validado_LAI.csv)
            # iteração na tabela aberta, a coluna "Se sim, link da regulamentação",
            # requisitando os links, por exemplo com requests
            # obtido o doc para rio branco, salvar o doc em LAI/dados_brutos
            # UF_nome_SIGLA-DA-LEI.pdf