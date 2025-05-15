import PyPDF2
import re
import os

path = './PDFs'
qt_arquivos = 0
for subpath in os.listdir(path): #Para 
    pdf_path = os.path.join(path, subpath)
    lista_arquivos = os.listdir(pdf_path)
    def extract_data(nome_arquivo):
        print(f"\n{nome_arquivo} processado...")

        with open(f"{pdf_path}/{nome_arquivo}", "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or "-"
                print("***** TEXTO DO PDF *****\n", text)
        if not text:
            print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
            return None
        #print(pdf_path)

        dados = {}  # Dicionário para armazenar todos os dados extraídos

        if "Flori" in subpath:
            # Número da Nota Fiscal Florianópolis
            numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", text)
            dados["Numero_NFSe"] = numero_nota_match.group(1).strip() if numero_nota_match else None

        elif "SP" in subpath:
            # Número da Nota Fiscal SP
            numero_nota_match = re.search(r"R\$\s*0,00(\d+)", text)
            dados["Numero_Nota"] = numero_nota_match.group(1).strip() if numero_nota_match else None

        elif "Cotia" in subpath:
            # Número da Nota Fiscal COTIA
            numero_nota_match = re.search(r"Nota:\s*(\d+)", text)
            dados["Numero_Nota"] = numero_nota_match.group(1).strip() if numero_nota_match else None

        elif "SBC" in subpath:
            # Número da Nota Fiscal SBC
            numero_nota_match = re.search(r"Competência(\d+)", text)
            dados["Numero_Nota"] = numero_nota_match.group(1).strip() if numero_nota_match else None

        else:
            # Número da Nota Fiscal Barueri
            numero_nota_match = re.search(r"SERVICOS E FATURA\s*Número da Nota\s*(\d+)", text)
            dados["Numero_Nota"] = numero_nota_match.group(1).strip() if numero_nota_match else None
        #Funciona SP e Floripa

        # Data emissão - Testar para todos
        data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)  # Ajuste aqui
        dados["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None  # Ajuste aqui

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
        if "Cotia" in subpath:
            valor_total_match = re.search(r"TOTAL DA NOTA =  R\$\s*([\d.,]+)", text)
        elif "Barueri" in subpath:
            valor_total_match = re.search(r"VALOR TOTAL DA NOTA\s*([R\$]?\s*[\d\.]+,\d{2})", text)
        elif "SBC" in subpath:
            valor_total_match = re.search(r"Valor\s+dos\s+Serviços\s+R\$\s*(\d+,\d{2})\s+Valor Total da Nota:", text)
        else:
            valor_total_match = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", text)
        dados["Valor_Total"] = valor_total_match.group(1).strip() if valor_total_match else None
        
        #Lista de CNPJs
        cnpj_list = re.findall(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", text)
        if cnpj_list:
            dados["CNPJ_do_Prestador"] = cnpj_list[0]
            if len(cnpj_list) > 1:
                dados["CNPJ_do_Tomador"] = cnpj_list[1]
            else:
                dados["CNPJ_do_Tomador"] = None
        else:
            dados["CNPJ_do_Prestador"] = None
            dados["CNPJ_do_Tomador"] = None

        return dados

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