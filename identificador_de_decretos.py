
for entry in os.scandir(directory):  # LAI, LGD, etc
    if not entry.is_file():  # LAI
        for entry in os.scandir(directory): # dados_extraidos
            # para cada documento txt existente em dados_extraidos
                # recortar o texto da regulamentação da lei que estara no meio de outros
                # textos do Diário Oficial

                    # uma possibilidade de automatizar o recorte é usando a API
                    # https://www.datacamp.com/pt/tutorial/a-beginners-guide-to-chatgpt-api
                    # prompt: reconheça e separe a regulamentação da lei tal nesse texto

                    # pensar em outras possibilidades de recortar

                    # tendo o recorte, tem que salvar o texto dentro do dir textos_completos