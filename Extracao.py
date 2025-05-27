import re

def extrai_numero_nota_pdf_imagem(texto):
    #print("Entrou em numero nota")
    # Número da Nota
    numero_nota = None
    numero_nota_match = re.search(r'''
    (?:
        s:\s?=\s* |         # Pode ser "s: =" ou "s: =" (com ou sem espaço extra)
        Barueri\s* |        # A palavra "Barueri"
        os\s+qo\s* |        # A sequência "os qo"
        ano:\s*=\s* |       # "ano: ="
        no;\s+É\s* |        # "no; É"
        qi\s* |             # "qi"
        nos\s+O\s* |        # "nos O"
        one\s+ |            # "one "
        “\s*Co\s* |          # "“ Co"
        O\s+a\s* |          # "O a"
        O\s+asse\s* |       # "O asse"
        O\s+ses\s* |        # "O ses"
        ana\s* |            # "ana"
        NFS-e\s* |
        Ciao:\s* # "Ciao:"
    )
    ([^\s]+)                # Captura um ou mais caracteres que não sejam espaço
''', texto, re.DOTALL | re.VERBOSE) # Use re.DOTALL e re.VERBOSE (ou re.X)
    if numero_nota_match:
        numero_nota = numero_nota_match.group(1).strip()
        #print("============================ 0",numero_nota)
        return numero_nota
    else:
        numero_nota_match = re.search(r'SÃO PAULO (\d+)', texto, re.DOTALL)
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
            #print("============================ 1",numero_nota)
            return numero_nota
        else:
            numero_nota_match = re.search(r"SÃO PAULO \[\s*(\d+)\s*", texto)
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
                #print("============================ 2",numero_nota)
                return numero_nota
            else:
                numero_nota_match = re.search(r'JANEIRO (\d+)', texto, re.DOTALL)
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                    #print("============================ 3",numero_nota)
                    return numero_nota
                else:
                    numero_nota_match = re.search(r'SANTA\s*—\s*(\d+)', texto, re.DOTALL)
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                        #print("============================ 4",numero_nota)
                        return numero_nota
                    else:
                        numero_nota_match = re.search(r'NOTA\s*R PADRE ANCHIETA, 1150 (\d+)', texto, re.DOTALL)
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
                            #print("============================ 5",numero_nota)
                            return numero_nota
                        else:
                            numero_nota = None
    return numero_nota
    #dados_nf["Numero_Nota"] = numero_nota

def extrai_numero_nota_pdf_selecionavel(texto):
    #print("Entrou em numero nota selecionavel")
    # Número da Nota
    numero_nota = None
    numero_nota_match = re.search(r"\s*(\d{3})NFS-e", texto, re.DOTALL) #Jundiai
    if numero_nota_match:
        numero_nota = numero_nota_match.group(1).strip()
        #print("============================ 0",numero_nota)
        return numero_nota
    else:
        numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", texto, re.DOTALL) #Flori
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
            #print("============================ 1",numero_nota)
            return numero_nota
        else:
            numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto, re.DOTALL) # SP
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
                #print("============================ 2",numero_nota)
                return numero_nota
            else:
                numero_nota_match = re.search(r"Nota:\s*(\d+)", texto, re.DOTALL) # Cotia
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                    #print("============================ 3",numero_nota)
                    return numero_nota
                else:
                    numero_nota_match = re.search(r"Competência(\d+)", texto, re.DOTALL) # SBC
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                        #print("============================ 4",numero_nota)
                        return numero_nota
                    else:
                        numero_nota_match = re.search(r"SERVICOS E FATURA\s*Número da Nota\s*(\d+)", texto, re.DOTALL) # Barueri
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
                            #print("============================ 5",numero_nota)
                            return numero_nota
                        else:
                            numero_nota_match = re.search(r"Competência(\s*\d+)", texto, re.DOTALL) # Campinas
                            if numero_nota_match:
                                numero_nota = numero_nota_match.group(1).strip()
                                #print("============================ 6",numero_nota)
                                return numero_nota
                            else:
                                numero_nota_match = re.search(r"Número da nota[\s\S]*?(\d+)", texto, re.DOTALL) # Campo Grande
                                if numero_nota_match:
                                    numero_nota = numero_nota_match.group(1).strip()
                                    #print("============================ 7",numero_nota)
                                    return numero_nota
                                else:
                                    numero_nota_match = re.search(r"FAZENDA\s*(\d+)", texto, re.DOTALL) # Campo Grande
                                    if numero_nota_match:
                                        numero_nota = numero_nota_match.group(1).strip()
                                        #print("============================ 8",numero_nota)
                                        return numero_nota
                                    else:
                                        numero_nota_match = re.search(r"FAZENDA\s*(\d+)", texto, re.DOTALL) # Campo Grande
                                        if numero_nota_match:
                                            numero_nota = numero_nota_match.group(1).strip()
                                            #print("============================ 9",numero_nota)
                                            return numero_nota
                                        else:
                                            numero_nota_match = re.search(r"Número Nota\s*\n\s*(\d+)", texto, re.DOTALL)
                                            if numero_nota_match:
                                                numero_nota = numero_nota_match.group(1).strip()
                                                #print("============================ 10", numero_nota)
                                                return numero_nota
                                            else:
                                                numero_nota_match = re.search(r"N[º°]?:\s*(\d+/\d+)", texto, re.DOTALL)
                                                if numero_nota_match:
                                                    numero_nota = numero_nota_match.group(1).strip()
                                                    numero_nota = numero_nota.replace('/','')
                                                    #print("============================ 11", numero_nota)
                                                    return numero_nota
                                                else:
                                                    numero_nota_match = re.search(r"NFE\s*[Nn][oº]\s*(\d+)", texto, re.DOTALL)
                                                    if numero_nota_match:
                                                        numero_nota = numero_nota_match.group(1).strip()
                                                        numero_nota = numero_nota.replace('/','')
                                                        #print("============================ 11", numero_nota)
                                                        return numero_nota
                                                    else:
                                                        numero_nota_match = re.search(r":NFS-e:\s*(\d+)", texto, re.DOTALL | re.IGNORECASE)
                                                        if numero_nota_match:
                                                            numero_capturado = numero_nota_match.group(1).strip()
                                                            numero_nota = re.match(r'^\d+', numero_capturado).group(0)
                                                            #print("============================ 12", numero_nota)
                                                            return numero_nota
                                                        else:
                                                            numero_nota_match = re.search(r"Nº Nota:\s*(\d+)", texto, re.DOTALL)
                                                            if numero_nota_match:
                                                                numero_nota = numero_nota_match.group(1).strip()
                                                                #print("============================ 13", numero_nota)
                                                                return numero_nota
                                                            else:
                                                                numero_nota_match = re.search(r"(\d+)\s*Número", texto, re.DOTALL)
                                                                if numero_nota_match:
                                                                    numero_nota = numero_nota_match.group(1).strip()
                                                                    #print("============================ 14", numero_nota)
                                                                    return numero_nota
                                                                else:
                                                                    numero_nota_match = re.search(r"\s*(\d+)\/", texto, re.DOTALL)
                                                                    if numero_nota_match:
                                                                        numero_nota = numero_nota_match.group(1).strip()
                                                                        #print("============================ 15", numero_nota)
                                                                        return numero_nota
                                                                    else:
                                                                        numero_nota = None
                                                                        return numero_nota
    #dados_nf["Numero_Nota"] = numero_nota

def extrai_data_emissao(texto):
    #print("Entrou em emissao")
    # Data de Emissão
    data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})|(\d{2}[\/](?:[a-zA-Z]{3})[\/]\d{4})", texto, re.DOTALL)
    if data_emissao_match:
        if data_emissao_match.group(0).strip() != '':
            data_emissao = data_emissao_match.group(0).strip()
            #print("Grupo 0", data_emissao)
            return data_emissao
        else:
            data_emissao = data_emissao_match.group(1).strip()
            #print("Grupo 1", data_emissao)
            return data_emissao
    else:
        data_emissao = None
        #print("None", data_emissao)
        return data_emissao

def extrai_Cnpjs(texto):
    #print("Entrou em CNPJs")
    def limpar_ocr_erros_comuns(texto_original):
        texto_limpo = texto_original.replace('O', '0') # Letra O por número zero
        return texto_limpo
    texto_processado = limpar_ocr_erros_comuns(texto)
    cnpjs_encontrados = []
    # Regex para CNPJs formatados (ex: 00 . 000 . 000 / 0000 - 00)
    cnpj_formatado_re = r"(\d{2}\s?\.\s?\d{3}\s?\.\s?\d{3}\s?/\s?\d{4}\s?-\s?\d{2})"
    matches_formatados = re.findall(cnpj_formatado_re, texto_processado)
    for cnpj_str in matches_formatados:
        cnpj_limpo = re.sub(r'[./\s-]', '', cnpj_str) # Remove todos os separadores e espaços
        # Adiciona a validação para ignorar CNPJs com 8 zeros no início
        if len(cnpj_limpo) == 14 and cnpj_limpo.isdigit() and not cnpj_limpo.startswith('00000000'):
            cnpjs_encontrados.append(cnpj_limpo)
    # Regex para CNPJs não formatados (14 dígitos consecutivos)
    cnpj_nao_formatado_re = r"(\d{14})\b"
    matches_nao_formatados = re.findall(cnpj_nao_formatado_re, texto_processado)
    for cnpj_str in matches_nao_formatados:
        # Adiciona a validação para ignorar CNPJs com 8 zeros no início
        if len(cnpj_str) == 14 and cnpj_str.isdigit() and not cnpj_str.startswith('000000'):
            cnpjs_encontrados.append(cnpj_str)

    cnpjs_unicos = []
    for cnpj in cnpjs_encontrados:
        if cnpj not in cnpjs_unicos:
            cnpjs_unicos.append(cnpj)
    if cnpjs_unicos:
        cnpj_prestador = cnpjs_unicos[0]
        #dados_nf["CNPJ_Prestador"] = cnpjs_unicos[0]
        if len(cnpjs_unicos) > 1:
            cnpj_tomador = cnpjs_unicos[1]
            #dados_nf["CNPJ_Tomador"] = cnpjs_unicos[1]
        else:
            cnpj_tomador = None
            #dados_nf["CNPJ_Tomador"] = None # Não encontrou um segundo CNPJ
    else:
        cnpj_prestador = None
        cnpj_tomador = None
        #dados_nf["CNPJ_Prestador"] = None
        #dados_nf["CNPJ_Tomador"] = None
    return cnpj_prestador, cnpj_tomador

def extrai_pedido_e_contrato(texto):
    #print("Entrou em Pedido e contrato")
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
    
    #num_pedido = None
    #num_contrato = None
    for item_na_descricao in descricao:
        if not num_pedido:
            num_pedido = buscar_numero(item_na_descricao, pedidos)
        if not num_contrato:
            num_contrato = buscar_numero(item_na_descricao, contratos)
    if num_pedido == None:
        pedido = ''
        #dados_nf["Pedido"] = ''
    else:    
        pedido = num_pedido
        #dados_nf["Pedido"] = num_pedido
    if num_contrato == None:
        contrato =  ''
        #dados_nf["Contrato"] = ''
    else:
        contrato = num_contrato
        #dados_nf["Contrato"] = num_contrato
    return pedido, contrato

def extrai_valores(texto):
    #print("Entrou em valores")
    # Valores
    valor_total = None
    valor_total_match = re.search(r"TOTAL DA NOTA =  R\$\s*([\d.,]+)", texto, re.DOTALL)
    if valor_total_match:
        valor_total = valor_total_match.group(1).strip()
        return valor_total
    else:
        valor_total_match = re.search(r"VALOR TOTAL DA NOTA\s*([R\$]?\s*[\d\.]+,\d{2})", texto, re.DOTALL)
        if valor_total_match:
            valor_total = valor_total_match.group(1).strip()
            return valor_total
        else:
            valor_total_match = re.search(r"Valor\s+dos\s+Serviços\s+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s+Valor Total da Nota:", texto, re.DOTALL)
            if valor_total_match:
                valor_total = valor_total_match.group(1).strip()
                return valor_total
            else:
                valor_total_match = re.search(r"VALOR TOTAL DA NOTA = R\$\s*([\d.,]+)", texto, re.DOTALL)
                if valor_total_match:
                    valor_total = valor_total_match.group(1).strip()
                    return valor_total
                else:
                    valor_total_match = re.search(r'[Vv]ALOR TOTAL RECEBIDO.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                    if valor_total_match:
                        valor_total = valor_total_match.group(1).strip()
                        return valor_total
                    else:
                        valor_total_match = re.search(r'[Vv]ALOR TOTAL.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                        if valor_total_match:
                            valor_total = valor_total_match.group(1).strip()
                            return valor_total
                        else:
                            valor_total_match = re.search(r'TOTAL DO SERVIÇO = .*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                            if valor_total_match:
                                valor_total = valor_total_match.group(1).strip()
                                return valor_total
                            else:
                                valor_total_match = re.search(r'VALOR DA NOTA = .*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                                if valor_total_match:
                                    valor_total = valor_total_match.group(1).strip()
                                    return valor_total
                                else:
                                    valor_total_match = re.search(r'VALOR DOS SERVIÇOS: R\$\s*([\d\.,]+)', texto, re.DOTALL)
                                    if valor_total_match:
                                        valor_total = valor_total_match.group(1).strip()
                                        return valor_total
                                    else:
                                        valor_total_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+\d{1,3}(?:\.\d{3})*,\d{2}VALOR TOTAL', texto)
                                        if valor_total_match:
                                            valor_total = valor_total_match.group(1).strip()
                                            return valor_total
                                        else:
                                            valor_total_match = re.search(r'((?<=\n)\d{1,3}(?:\.\d{3})*,\d{2})', texto, re.DOTALL)
                                            if valor_total_match:
                                                valor_total = valor_total_match.group(1).strip()
                                                return valor_total
                                            else:
                                                valor_servicos_match = re.search(r"Valor dos serviços:\s*R\$\s*([\d\.,]+)", texto, re.DOTALL)
                                                if valor_servicos_match:
                                                    valor_total = valor_servicos_match.group(1).strip()
                                                    return valor_total

    #dados_nf["Valor_Total"] = valor_total if valor_total_match else None
    valor_nf = valor_total if valor_total_match else None
    return valor_total
