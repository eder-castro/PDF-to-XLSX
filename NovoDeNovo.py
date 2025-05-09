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

    valor_total_match = re.search(r"VALOR TOTAL DA NOTA\s*([R\$]?\s*[\d\.]+,\d{2})", text)
    dados["Valor_Total"] = valor_total_match.group(1).strip() if valor_total_match else None

    # Prestador de Serviços
    dados["Nome_Prestador"] = None
    prestador_bloco_match = re.search(r"Prestador de Serviços\s+([A-Za-zÀ-ú\s.' ]+LTDA)(?:\s*\n|$)", text, re.DOTALL)
    if prestador_bloco_match:
        prestador_bloco = prestador_bloco_match.group(1)
        nome_prestador_match = re.search(r"([A-Za-zÀ-ú\s.'-]+)", prestador_bloco)
        dados["Nome_Prestador"] = nome_prestador_match.group(1).strip() if nome_prestador_match else None
    
    # Tomador de Serviços
    tomador_bloco_match = re.search(r"(?<=Valor Total)([A-Za-zÀ-ú\s.'-]+(?: LTDA)?)\s*(?=\d{2}\.\d{3}\.\d{3})", text, re.DOTALL)
    print(tomador_bloco_match)
    if tomador_bloco_match:
        tomador_bloco = tomador_bloco_match.group(1)
        nome_tomador_match = re.search(r"([A-Za-zÀ-ú\s.'-]+)", tomador_bloco)
        dados["Nome_Tomador"] = nome_tomador_match.group(1).strip() if nome_tomador_match else None
    

    return dados

# Exemplo de uso:
pdf_path = './PDFs/Barueri'
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