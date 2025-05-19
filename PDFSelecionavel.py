import PyPDF2
import re
import os

path = './PDFs'
qt_arquivos = 0
for subpath in os.listdir(path):
    pdf_path = os.path.join(path, subpath)
    lista_arquivos = os.listdir(pdf_path)
    print(pdf_path)
    def extract_data(nome_arquivo):
        #print(f"{nome_arquivo} processado...")

        with open(f"{pdf_path}/{nome_arquivo}", "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or "-"
                #print("***** TEXTO DO PDF *****\n", texto)
        if not texto:
            print(f"[AVISO] Não foi possível extrair texto do PDF: {nome_arquivo}")
            return None
        #print(pdf_path)

        dados_nf = {}  # Dicionário para armazenar todos os dados extraídos

        # Número da Nota
        numero_nota = None
        numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", texto, re.DOTALL) #Flori
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip() 
        else:
            numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto, re.DOTALL) # SP
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
            else:
                numero_nota_match = re.search(r"Nota:\s*(\d+)", texto, re.DOTALL) # Cotia
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                else:
                    numero_nota_match = re.search(r"Competência(\d+)", texto, re.DOTALL) # SBC
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                    else:
                        numero_nota_match = re.search(r"SERVICOS E FATURA\s*Número da Nota\s*(\d+)", texto, re.DOTALL) # Barueri
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
        dados_nf["Numero_Nota"] = numero_nota

        # Data emissão - Testar para todos
        data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)  # Ajuste aqui
        dados_nf["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None  # Ajuste aqui

        #Lista de CNPJs
        cnpj_list = re.findall(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", texto)
        if cnpj_list:
            dados_nf["CNPJ_Prestador"] = cnpj_list[0]
            if len(cnpj_list) > 1:
                dados_nf["CNPJ_Tomador"] = cnpj_list[1]
            else:
                dados_nf["CNPJ_Tomador"] = None
        else:
            dados_nf["CNPJ_Prestador"] = None
            dados_nf["CNPJ_Tomador"] = None

        # Pedido e Contrato
        descricao = [texto]
        pedidos = ["42000", "43000", "45000"]
        contratos = ["47000", "48000"]
        num_pedido = None
        num_contrato = None
        def buscar_numero(item, termos):
            if isinstance(item, str):
                for termo in termos:
                    for palavra in item.split():
                        if termo in palavra:
                            potential = palavra[palavra.find(termo):palavra.find(termo) + 10]
                            if len(potential) == 10 and potential.isdigit():
                                return potential
            elif isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, str):
                        for termo in termos:
                            if termo in sub_item:
                                potential = sub_item.strip()
                                if len(potential) == 10 and potential.isdigit():
                                    return potential
            elif isinstance(item, dict):
                for valor in item.values():
                    if isinstance(valor, str):
                        for termo in termos:
                            if termo in valor:
                                potential = valor.strip()
                                if len(potential) == 10 and potential.isdigit():
                                    return potential
            return None
        num_pedido = None
        num_contrato = None
        for item_na_descricao in descricao:
            if not num_pedido:
                num_pedido = buscar_numero(item_na_descricao, pedidos)
            if not num_contrato:
                num_contrato = buscar_numero(item_na_descricao, contratos)
        if num_pedido == None:
            dados_nf["Pedido"] = ''
        else:    
            dados_nf["Pedido"] = num_pedido
        if num_contrato == None:
            dados_nf["Contrato"] = ''
        else:
            dados_nf["Contrato"] = num_contrato

        # Valores
        valor_total = None
        valor_total_match = re.search(r"TOTAL DA NOTA =  R\$\s*([\d.,]+)", texto, re.DOTALL)
        if valor_total_match:
            valor_total = valor_total_match.group(1).strip()
        else:
            valor_total_match = re.search(r"VALOR TOTAL DA NOTA\s*([R\$]?\s*[\d\.]+,\d{2})", texto, re.DOTALL)
            if valor_total_match:
                valor_total = valor_total_match.group(1).strip()
            else:
                valor_total_match = re.search(r"Valor\s+dos\s+Serviços\s+R\$\s*(\d+,\d{2})\s+Valor Total da Nota:", texto, re.DOTALL)
                if valor_total_match:
                    valor_total = valor_total_match.group(1).strip()
                else:
                    valor_total_match = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", texto, re.DOTALL)
                    if valor_total_match:
                        valor_total = valor_total_match.group(1).strip()
                    else:
                        valor_total_match = re.search(r'[Vv]ALOR TOTAL RECEBIDO.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                        if valor_total_match:
                            valor_total = valor_total_match.group(1).strip()
                        else:
                            valor_total_match = re.search(r'[Vv]ALOR TOTAL.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                            if valor_total_match:
                                valor_total = valor_total_match.group(1).strip()
                            else:
                                valor_total_match = re.search(r'TOTAL DO SERVIÇO = .*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                                if valor_total_match:
                                    valor_total = valor_total_match.group(1).strip()
        dados_nf["Valor_Total"] = valor_total_match.group(1).strip() if valor_total_match else None        

        # Nome do Arquivo
        dados_nf["Nome_Arquivo"] = nome_arquivo

        print(dados_nf)
        return dados_nf

    for arquivo in lista_arquivos:
        if arquivo.lower().endswith(".pdf"):
            extracted_data = extract_data(arquivo)  # Alterei o nome da função para algo mais genérico
            qt_arquivos += 1
            # if extracted_data:
            #     print("OK")
            #     # for key, value in extracted_data.items():
            #     #     print(f"{key}: {value}")
            # else:
            #     print("Não foi possível extrair os dados.")
print(qt_arquivos, " arquivos processados...")