import os
import pymupdf
from pdf2image import convert_from_path
import pytesseract
from bs4 import BeautifulSoup

POPPLER_PATH = "C:\poppler-25.07.0\Library\bin"
LAWS = ["LAI", "LGD", "LGPD", "MROSC"]
TERRITORY_TYPES = ["capital","estado"]
DIRECTORY = os.getcwd()
DADOS_BRUTOS_DIRECTORY = "//dados_brutos"
DADOS_EXTRAIDOS_DIRECTORY = "//dados_extraidos"
MIN_TEXT_RATIO = 0.1

def html_to_text(html_path: str):
    try:
        with open(html_path, 'r', encoding = 'utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'lxml')
            body_tag = soup.find('body')
            if body_tag :
                text_content = body_tag.get_text(separator='\n', strip=True)
            else:
                text_content = "Extração não realizada"
            return (text_content)
    except Exception as e:
        print(e)

def save_text_to_file(content: str, full_file_path: str):
    with open(full_file_path, 'w', encoding='utf_8') as text_output:
        text_output.write(content)

def check_and_extract_text_from_pdf(full_file_path: str):
    total_area = 0.0
    total_text_area = 0.0
    text_ratio = 0
    text = ""

    try:
        with pymupdf.open(full_file_path) as doc:
            for page_num, page in enumerate(doc):
                text += page.get_text("text")
                total_area += abs(page.rect)
                text_blocks = page.get_text("blocks")
                text_area = 0.0
                for block in text_blocks:
                    x0, y0, x1, y1, content, block_type, *rest = block
                    if block_type == 0:
                        rect = pymupdf.Rect(x0, y0, x1, y1)
                        text_area += rect
        
                total_text_area += text_area
        
        if(total_area) > 0:
            text_ratio = (total_text_area / total_area)

        if(text_ratio >= MIN_TEXT_RATIO):
            return text            

        return None

    except Exception as e:
        print(f"Erro ao extrair texto de arquivo pdf: {e}")
        return None 

def convert_pdf_image_to_text(full_file_path: str):
    text = ""
    try:
        images = convert_pdf_image_to_text(full_file_path, poppler_path = POPPLER_PATH)
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image, lang="por")
            text += page_text + "\n"

        return text 

    except Exception as e:
        print(f"Erro ao executar OCR em arquivo pdf: {e}")

    

for entry in os.scandir(DIRECTORY):
    if(entry.name in LAWS):
        for subentry in os.scandir(entry):
            if(os.path.isdir(subentry) and subentry.name in TERRITORY_TYPES):
                dados_brutos_full_path = subentry.path + "//" + DADOS_BRUTOS_DIRECTORY
                dados_extraidos_full_path = subentry.path + "//" + DADOS_EXTRAIDOS_DIRECTORY
                for file in os.scandir(dados_brutos_full_path):                    
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
                                converted_text = check_and_extract_text_from_pdf(file.path)
                                if converted_text == None or converted_text == "":
                                    print(file.name, "Texto vazio, executando OCR")  
                                    converted_text = convert_pdf_image_to_text(file.path)
                                if converted_text != None and converted_text != "":
                                    save_text_to_file(converted_text, dados_extraidos_full_file_path)
                                else:
                                    print(file.name, "Erro ao converter pdf")                                                           
                            case ".html":
                                print(file.name, "Convertendo html para txt")
                                converted_text = html_to_text(file.path)
                                save_text_to_file(converted_text, dados_extraidos_full_file_path)
                            case ".htm":
                                print(file.name, "Convertendo html para txt")
                                converted_text = html_to_text(file.path)
                                save_text_to_file(converted_text, dados_extraidos_full_file_path)
                            case _:
                                print(file.name, "Tipo de arquivo não identificado")



    
                                      