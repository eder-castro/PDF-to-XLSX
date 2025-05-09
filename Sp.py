import PyPDF2
import re
import os

def extract_data(nome_arquivo):  # Alterei o nome da função para algo mais genérico
    print(f"\n{nome_arquivo} processado...")

    with open(f"{pdf_path}/{nome_arquivo}", "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Usar "" como fallback
            #print("***** TEXTO DO PDF *****\n", text)
    if not text:
        print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
        return None


    dados = {}  # Dicionário para armazenar todos os dados extraídos

    # Dados da Nota Fiscal
    numero_nota_match = re.search(r"R\$\s*0,00(\d+)", text)
    dados["Numero_Nota"] = numero_nota_match.group(1).strip() if numero_nota_match else None  # Ajuste aqui
    data_emissao_match = re.search(r"Data e Hora de Emissão\s*([\d/: ]+)", text)  # Ajuste aqui
    dados["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None  # Ajuste aqui

    # Prestador de Serviços
    dados["Nome_Prestador"] = None
    dados["CNPJ_Prestador"] = None
    prestador_bloco_match = re.search(r"PRESTADOR DE SERVIÇOS(.+?)TOMADOR DE SERVIÇOS", text, re.DOTALL)
    if prestador_bloco_match:
        prestador_bloco = prestador_bloco_match.group(1)
        nome_prestador_match = re.search(r"Municipio:([A-Za-zÀ-ú\s]+)\d", prestador_bloco)
        dados["Nome_Prestador"] = nome_prestador_match.group(1).strip() if nome_prestador_match else None
        dados["CNPJ_Prestador"] = re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", prestador_bloco).group(1) if re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", prestador_bloco) else None
    
    # Tomador de Serviços
    dados["Nome_Tomador"] = None
    dados["CNPJ_Tomador"] = None
    tomador_bloco_match = re.search(r"TOMADOR DE SERVIÇOS(.+?)UF:", text, re.DOTALL)
    if tomador_bloco_match:
        tomador_bloco = tomador_bloco_match.group(1)
        nome_tomador_match = re.search(r"CNPJ/CPF:.*?([A-Za-zÀ-ú\s]+?)(?:\.\s*Nome/Razão Social:|(?=\s*Nome/Razão Social:))", tomador_bloco)
        dados["Nome_Tomador"] = nome_tomador_match.group(1).strip() if nome_tomador_match else None
        dados["CNPJ_Tomador"] = re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", tomador_bloco).group(1) if re.search(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", tomador_bloco) else None

    # Pedido e Contrato
    descricao = [text]
    pedidos = ["42000", "43000", "45000"]
    contratos = ["47000", "48000"]
    num_pedido = None
    num_contrato = None

    for item_na_descricao in descricao:
        if isinstance(item_na_descricao, str):
            for pedido in pedidos:
                for palavra in item_na_descricao.split():
                    if pedido in palavra:
                        num_pedido = palavra[palavra.find(pedido):palavra.find(pedido)+10]
            for contrato in contratos:
                for palavra in item_na_descricao.split():
                    if contrato in palavra:
                        num_contrato = palavra[palavra.find(contrato):palavra.find(contrato)+10]
        elif isinstance(item_na_descricao, list):
            for item_da_lista in item_na_descricao:
                if isinstance(item_da_lista, str):
                    for pedido in pedidos:
                        if pedido in item_da_lista:
                            num_pedido = item_da_lista
                            break
                    if num_pedido:
                        break
                elif isinstance(item_da_lista, dict):
                    for vlr in item_da_lista.values():
                        if isinstance(vlr, str):
                            for pedido in pedidos:
                                if pedido in vlr:
                                    num_pedido = vlr
                                    break
                            if num_pedido:
                                break
                    if num_pedido:
                        break
    dados["Pedido"] = num_pedido
    dados["Contrato"] = num_contrato

    # Valores
    valor_total_match = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text)  # Ajuste aqui
    dados["Valor_Total"] = valor_total_match.group(1).strip() if valor_total_match else None  # Ajuste aqui

    return dados

# Exemplo de uso:
pdf_path = './PDFs/Barueri'
lista_arquivos = os.listdir(pdf_path)
qt_arquivos = 0

for arquivo in lista_arquivos:
    if arquivo.lower().endswith(".pdf"):
        extracted_data = extract_data(arquivo)  # Alterei o nome da função para algo mais genérico
        qt_arquivos += 1
        if extracted_data:
            for key, value in extracted_data.items():
                print(f"{key}: {value}")
        else:
            print("Não foi possível extrair os dados.")
print(qt_arquivos, " arquivos processados...")