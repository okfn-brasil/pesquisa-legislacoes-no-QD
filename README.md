Encontros às quintas, 18h.

- [] iterar nas tabelas de validação para baixar os documentos
  - um script só, navega o repositório atrás dos csvs nomeados por "validado" que faz isso para os 4 diretórios das leis e a saída dos arquivos baixados 
  ficam no subdiretório dados_brutos/ 
- [] iterar nos documentos baixados para obter o texto completo da lei
- [] ETL nos dados
  - Fase 1: obter os dados textuais
    - HTML -> TXT: remover as tags do HTML (dicas: Beatiful Soup)
    - PDF -> TXT: extração de texto de PDF (dicas: PyMuPDF, PDFMiner, pypdf)
    - doc/docx -> TXT: extração de texto de doc/docx
    - Imagem -> TXT: ApacheTika, faz OCR. Ao encontrar casos assim, a gente volta a conversar.
    - TXT: os documentos que estão no QD (exemplo abaixo) já tem a versão TXT deles, é só trocar o ".pdf" para ".txt".
      - https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3106200/2024-01-19/2cf0586f900ff293b2128686e31671fb149dbb22.pdf
      - https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3106200/2024-01-19/2cf0586f900ff293b2128686e31671fb149dbb22.txt
  - Fase 2: obter apenas o texto da regulamentação no meio de todo documento
    - fase opcional, pode não ser necessária sempre

- padrão de nomenclatura dos arquivos:
  - para capitais: nome-da-capital_sigla-da-lei
  - para estados: nome-do-estado_sigla-da-lei

- coleta.py: Daniel
- extracao.py: Gustavo
- identificador_de_decretos.py: Rafael
