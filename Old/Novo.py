import PyPDF2
import re
import os

def extract_data_layout5(nome_arquivo):
    print(f"{nome_arquivo} processado...")

    with open(f"PDFs/Florianopolis/{nome_arquivo}", "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Usar "" como fallback
    if not text:
        print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
        return None

    dados = {}  # Dicionário para armazenar todos os dados extraídos

    # Dados da Nota Fiscal (Manter para referência, mas não vamos imprimir ainda)
    dados["Numero_NFSe"] = re.search(r"Número da NFS-e\s*(\d+)", text).group(1) if re.search(r"Número da NFS-e\s*(\d+)", text) else None
    dados["Data_Emissao"] = re.search(r"Data e Hora de Emissão\s*([\d/: ]+)", text).group(1) if re.search(r"Data e Hora de Emissão\s*([\d/: ]+)", text) else None

    # Prestador de Serviços
    prestador_bloco_match = re.search(r"PRESTADOR DE SERVIÇOS(.+?)TOMADOR DE SERVIÇOS", text, re.DOTALL)
    if prestador_bloco_match:
        prestador_bloco = prestador_bloco_match.group(1)
        print("\n--- PRESTADOR DE SERVIÇOS BLOCO ---\n")
        print(prestador_bloco)
    else:
        print("\n--- PRESTADOR DE SERVIÇOS BLOCO NÃO ENCONTRADO ---\n")

    # Tomador de Serviços
    tomador_bloco_match = re.search(r"TOMADOR DE SERVIÇOS(.+?)VALOR TOTAL DA NOTA", text, re.DOTALL)
    if tomador_bloco_match:
        tomador_bloco = tomador_bloco_match.group(1)
        print("\n--- TOMADOR DE SERVIÇOS BLOCO ---\n")
        print(tomador_bloco)
    else:
        print("\n--- TOMADOR DE SERVIÇOS BLOCO NÃO ENCONTRADO ---\n")

    # Valores (Manter para referência, mas não vamos imprimir ainda)
    dados["Valor_Total"] = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text).group(1).strip() if re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text) else None

    return dados

# Exemplo de uso:
pdf_path = './PDFs/Florianopolis'
lista_arquivos = os.listdir(pdf_path)
qt_arquivos = 0

for arquivo in lista_arquivos:
    if arquivo.lower().endswith(".pdf"):
        extracted_data = extract_data_layout5(arquivo)
        if extracted_data:
            print("Dados Extraídos:")
            for key, value in extracted_data.items():
                print(f"{key}: {value}")
        else:
            print("Não foi possível extrair os dados.")