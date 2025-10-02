# percorrer os diretorios até chegar nos subdiretório dados brutos existente em cada um
# para cada documento dentro de dados_brutos, evoca uma biblioteca para extrair

for entry in os.scandir(directory):  # LAI, LGD, etc
    # se o nome do subdiretorio for dados_brutos
        # entra no diretório
            # para cada documento de dados_brutos:
                # if documento is pdf: extrai com pypdf -> txt
                # if documento is html: extrai com BS -> txt
                # if documento is txt: não precisa extração -> txt

                # fez a extração, guardou o txt em dados_extraidos