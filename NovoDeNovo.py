import PyPDF2
import re
import os

def extract_data(nome_arquivo): # Alterei o nome da função para algo mais genérico
    print(f"\n{nome_arquivo} processado...")

    with open(f"{pdf_path}/{nome_arquivo}", "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Usar "" como fallback
            print("***** TEXTO DO PDF *****\n", text)
    if not text:
        print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
        return None

    dados = {}  # Dicionário para armazenar todos os dados extraídos

    data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)  # Ajuste aqui
    dados["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None  # Ajuste aqui

    

    



    return dados

# Exemplo de uso:
pdf_path = './PDFs/Cotia'
lista_arquivos = os.listdir(pdf_path)
qt_arquivos = 0

for arquivo in lista_arquivos:
    if arquivo.lower().endswith(".pdf"):
        extracted_data = extract_data(arquivo) # Alterei o nome da função para algo mais genérico
        qt_arquivos += 1
        if extracted_data:
            for key, value in extracted_data.items():
                print(f"{key}: {value}")
        else:
            print("Não foi possível extrair os dados.")
print(qt_arquivos, " arquivos processados...")