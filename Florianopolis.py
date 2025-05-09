import PyPDF2
import re
import os

def extract_data_layout5(nome_arquivo):
    print(f"\n{nome_arquivo} processado...")

    with open(f"PDFs/Cotia/{nome_arquivo}", "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Usar "" como fallback
    if not text:
        print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
        return None

    dados = {}  # Dicionário para armazenar todos os dados extraídos

    # Dados da Nota Fiscal
    numero_nfse_match = re.search(r",..\s*(\d+)Número da NFS-e", text)
    dados["Numero_NFSe"] = numero_nfse_match.group(1).strip() if numero_nfse_match else None
    dados["Data_Emissao"] = re.search(r"Data e Hora de Emissão\s*([\d/: ]+)", text).group(1) if re.search(r"Data e Hora de Emissão\s*([\d/: ]+)", text) else None

    # Prestador de Serviços
    prestador_bloco_match = re.search(r"PRESTADOR DE SERVIÇOS(.+?)TOMADOR DE SERVIÇOS", text, re.DOTALL)
    if prestador_bloco_match:
        prestador_bloco = prestador_bloco_match.group(1)
        nome_prestador_match = re.search(r"UF:(.+)", prestador_bloco) # Ajuste aqui
        dados["Nome_Prestador"] = nome_prestador_match.group(1).strip() if nome_prestador_match else None
        dados["CNPJ_Prestador"] = re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", prestador_bloco).group(1) if re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", prestador_bloco) else None
    
    # Tomador de Serviços
    tomador_bloco_match = re.search(r"TOMADOR DE SERVIÇOS(.+?)VALOR TOTAL DA NOTA", text, re.DOTALL)
    if tomador_bloco_match:
        tomador_bloco = tomador_bloco_match.group(1)
        nome_tomador_match = re.search(r"UF:(.+)", tomador_bloco) # Ajuste aqui
        dados["Nome_Tomador"] = nome_tomador_match.group(1).strip() if nome_tomador_match else None
        dados["CNPJ_Tomador"] = re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", tomador_bloco).group(1) if re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", tomador_bloco) else None

    # Valores
    dados["Valor_Total"] = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text).group(1).strip() if re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text) else None

    return dados

# Exemplo de uso:
pdf_path = './PDFs/Cotia'
lista_arquivos = os.listdir(pdf_path)
qt_arquivos = 0

for arquivo in lista_arquivos:
    if arquivo.lower().endswith(".pdf"):
        extracted_data = extract_data_layout5(arquivo)
        qt_arquivos += 1
        if extracted_data:
            for key, value in extracted_data.items():
                print(f"{key}: {value}")
        else:
            print("Não foi possível extrair os dados.")
print(qt_arquivos, " arquivos processados...")