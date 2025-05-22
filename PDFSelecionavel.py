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
        numero_nota_match = re.search(r"\s*(\d{3})NFS-e", texto, re.DOTALL) #Jundiai
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
            #print("============================ 0",numero_nota)
        else:
            numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", texto, re.DOTALL) #Flori
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
                #print("============================ 1",numero_nota)
            else:
                numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto, re.DOTALL) # SP
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                    #print("============================ 2",numero_nota)
                else:
                    numero_nota_match = re.search(r"Nota:\s*(\d+)", texto, re.DOTALL) # Cotia
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                        #print("============================ 3",numero_nota)
                    else:
                        numero_nota_match = re.search(r"Competência(\d+)", texto, re.DOTALL) # SBC
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
                            #print("============================ 4",numero_nota)
                        else:
                            numero_nota_match = re.search(r"SERVICOS E FATURA\s*Número da Nota\s*(\d+)", texto, re.DOTALL) # Barueri
                            if numero_nota_match:
                                numero_nota = numero_nota_match.group(1).strip()
                                #print("============================ 5",numero_nota)
                            else:
                                numero_nota_match = re.search(r"Competência(\s*\d+)", texto, re.DOTALL) # Campinas
                                if numero_nota_match:
                                    numero_nota = numero_nota_match.group(1).strip()
                                    #print("============================ 6",numero_nota)
                                else:
                                    numero_nota_match = re.search(r"Número da Nota\s*(\d+)", texto, re.DOTALL) # Campo Grande
                                    if numero_nota_match:
                                        numero_nota = numero_nota_match.group(1).strip()
                                        #print("============================ 7",numero_nota)
                                    else:
                                        numero_nota_match = re.search(r"FAZENDA\s*(\d+)", texto, re.DOTALL) # Campo Grande
                                        if numero_nota_match:
                                            numero_nota = numero_nota_match.group(1).strip()
                                            #print("============================ 8",numero_nota)
                                        else:
                                            numero_nota_match = re.search(r"FAZENDA\s*(\d+)", texto, re.DOTALL) # Campo Grande
                                            if numero_nota_match:
                                                numero_nota = numero_nota_match.group(1).strip()
                                                #print("============================ 9",numero_nota)
        dados_nf["Numero_Nota"] = numero_nota

        # Data emissão - Testar para todos
        data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)  # Ajuste aqui
        dados_nf["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None  # Ajuste aqui

        # #Lista de CNPJs
        # cnpj_list = re.findall(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", texto)
        # if cnpj_list:
        #     dados_nf["CNPJ_Prestador"] = cnpj_list[0]
        #     if len(cnpj_list) > 1:
        #         dados_nf["CNPJ_Tomador"] = cnpj_list[1]
        #     else:
        #         dados_nf["CNPJ_Tomador"] = None
        # else:
        #     dados_nf["CNPJ_Prestador"] = None
        #     dados_nf["CNPJ_Tomador"] = None

        def limpar_ocr_erros_comuns(texto_original):
            #"""Substitui caracteres frequentemente confundidos pelo OCR."""
            texto_limpo = texto_original.replace('O', '0') # Letra O por número zero
            # Adicione mais substituições conforme for identificando erros comuns do OCR
            # texto = texto.replace('l', '1') # Letra l por número um
            # texto = texto.replace('B', '8') # Letra B por número oito
            return texto_limpo

        # Seu texto de exemplo (incluindo variações)
        # texto_original = """
        # CNPJ Prestador: 12.345.678/0001-90
        # CNPJ Tomador: 98.765.432 / 0001 - 21
        # CNPJ Sem Formato: 11223344556677
        # CNPJ Com O: 12.345.678/0O01-9O
        # Outro numero 123456789012345
        # CNPJ Teste: 22334455667788
        # """

        # 1. Limpeza inicial do texto de OCR
        texto_processado = limpar_ocr_erros_comuns(texto)

        # 2. Definição da REGEX combinada
        # Sua REGEX atualizada para CNPJ formatado já lida com espaços opcionais:
        # r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}\s?-\s?[\d]{2})"
        # Agora, vamos adicionar a opção para 14 dígitos sem formatação

        # REGEX para CNPJ formatado (já permite espaços ao redor de '-' com '\s?')
        # Podemos estender para permitir espaços também ao redor de '.' e '/' se necessário,
        # mas seu padrão atual já é bom para '-'
        #cnpj_formatado_pattern = r"(\d{2}\.?\s?\d{3}\.?\s?\d{3}/?\s?\d{4}\s?-\s?\d{2})"
        # Permiti:
        # \.?\s? para pontos e barras opcionais com espaços opcionais.
        # O '?' torna o ponto e a barra opcionais também, o que pode não ser o ideal se eles são obrigatórios.
        # Se eles forem obrigatórios, a sua REGEX original para formatados é melhor.
        # Vamos manter a sua original e adicionar a sem formatação.

        # Opção 1: Uma única REGEX poderosa
        # (Formato com pontos/barras/hífens E espaços opcionais OU 14 dígitos sem formatação)
        #cnpj_full_pattern = r"(\d{2}\.?\s?\d{3}\.?\s?\d{3}/?\s?\d{4}\s?-\s?\d{2}|\b\d{14}\b)"

        # OU, a melhor forma: Duas REGEXes e combinar resultados, com limpeza posterior
        # Isso é mais robusto porque a validação final será mais controlada.

        # Lista para armazenar os CNPJs válidos que encontrarmos
        cnpjs_encontrados = []

        # Primeira busca: CNPJs formatados (com ou sem espaços extras)
        # Ajustei ligeiramente sua REGEX para permitir espaços em todos os separadores, se necessário.
        # Se os pontos e barras são *sempre* obrigatórios e apenas hífens podem ter espaços, use sua original.
        # Se todos os separadores podem ter espaços, a seguinte é boa:
        cnpj_formatado_re = r"(\d{2}\s?\.\s?\d{3}\s?\.\s?\d{3}\s?/\s?\d{4}\s?-\s?\d{2})"
        matches_formatados = re.findall(cnpj_formatado_re, texto_processado)
        for cnpj_str in matches_formatados:
            # Limpa espaços e formatação para padronizar
            cnpj_limpo = re.sub(r'[./\s-]', '', cnpj_str) # Remove todos os separadores e espaços
            if len(cnpj_limpo) == 14 and cnpj_limpo.isdigit(): # Garante que são 14 dígitos
                cnpjs_encontrados.append(cnpj_limpo)

        # Segunda busca: CNPJs sem formatação (14 dígitos consecutivos)
        cnpj_nao_formatado_re = r"(\d{14})\b" # \b para garantir que não são parte de um número maior
        matches_nao_formatados = re.findall(cnpj_nao_formatado_re, texto_processado)
        for cnpj_str in matches_nao_formatados:
            if len(cnpj_str) == 14 and cnpj_str.isdigit(): # Validação extra
                cnpjs_encontrados.append(cnpj_str)


        # Remover duplicatas e manter a ordem de aparição (se desejar uma ordem consistente)
        # Uma maneira simples de remover duplicatas mantendo a ordem:
        cnpjs_unicos = []
        for cnpj in cnpjs_encontrados:
            if cnpj not in cnpjs_unicos:
                cnpjs_unicos.append(cnpj)

        # Agora, atribua aos dados_nf
        if cnpjs_unicos:
            dados_nf["CNPJ_Prestador"] = cnpjs_unicos[0]
            if len(cnpjs_unicos) > 1:
                # Sua lógica de `if cnpj_list[1] != cnpj_list[0]` é importante se o Prestador e Tomador
                # puderem ter o mesmo CNPJ mas você espera que o segundo seja diferente quando há 3 CNPJs.
                # Simplifiquei um pouco aqui, mas você pode readaptar.
                dados_nf["CNPJ_Tomador"] = cnpjs_unicos[1]
            else:
                dados_nf["CNPJ_Tomador"] = None # Não encontrou um segundo CNPJ
        else:
            dados_nf["CNPJ_Prestador"] = None
            dados_nf["CNPJ_Tomador"] = None

        #print(f"Texto original:\n{texto_original}")
        # print(f"Texto processado (após limpeza OCR):\n{texto_processado}")
        # print(f"CNPJs encontrados e validados: {cnpjs_unicos}")
        # print(f"Dados extraídos: {dados_nf}")


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
                valor_total_match = re.search(r"Valor\s+dos\s+Serviços\s+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s+Valor Total da Nota:", texto, re.DOTALL)
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
                                else:
                                    valor_total_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}VALOR TOTAL', texto)
                                    if valor_total_match:
                                        valor_total = valor_total_match.group(1).strip()
                                    else:
                                        valor_total_match = re.search(r'((?<=\n)\d{1,3}(?:\.\d{3})*,\d{2})', texto, re.DOTALL)
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