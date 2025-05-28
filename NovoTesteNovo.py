def extrai_documentos(texto):
    def limpar_ocr_erros_comuns(texto_original):
        # Substitui 'O' por '0' e remove caracteres indesejados comuns em OCR
        texto_limpo = texto_original.replace('O', '0')
        # Adicione outras substituições comuns aqui, se necessário (ex: 'l' por '1', 'B' por '8')
        return texto_limpo

    texto_processado = limpar_ocr_erros_comuns(texto)
    documentos_encontrados = []

    # Regex para CNPJs formatados (ex: 00.000.000/0000-00)
    cnpj_formatado_re = r"(\d{2}\s*\.\s*\d{3}\s*\.\s*\d{3}\s*\/\s*\d{4}\s*-\s*\d{2})"
    # Regex para CNPJs não formatados (14 dígitos consecutivos)
    cnpj_nao_formatado_re = r"\b(\d{14})\b"

    # Regex para CPFs formatados (ex: 000.000.000-00)
    cpf_formatado_re = r"(\d{3}\s*\.\s*\d{3}\s*\.\s*\d{3}\s*-\s*\d{2})"
    # Regex para CPFs não formatados (11 dígitos consecutivos)
    cpf_nao_formatado_re = r"\b(\d{11})\b"

    # Busca por CNPJs formatados
    matches_cnpj_formatados = re.findall(cnpj_formatado_re, texto_processado)
    for doc_str in matches_cnpj_formatados:
        doc_limpo = re.sub(r'[./\s-]', '', doc_str)
        if len(doc_limpo) == 14 and doc_limpo.isdigit() and not doc_limpo.startswith('00000000'):
            documentos_encontrados.append(doc_limpo)

    # Busca por CNPJs não formatados
    matches_cnpj_nao_formatados = re.findall(cnpj_nao_formatado_re, texto_processado)
    for doc_str in matches_cnpj_nao_formatados:
        if len(doc_str) == 14 and doc_str.isdigit() and not doc_str.startswith('00000000'):
            documentos_encontrados.append(doc_str)

    # Busca por CPFs formatados
    matches_cpf_formatados = re.findall(cpf_formatado_re, texto_processado)
    for doc_str in matches_cpf_formatados:
        doc_limpo = re.sub(r'[./\s-]', '', doc_str)
        if len(doc_limpo) == 11 and doc_limpo.isdigit() and not doc_limpo.startswith('000000000'): # Evitar CPF de '0'
            documentos_encontrados.append(doc_limpo)

    # Busca por CPFs não formatados
    matches_cpf_nao_formatados = re.findall(cpf_nao_formatado_re, texto_processado)
    for doc_str in matches_cpf_nao_formatados:
        if len(doc_str) == 11 and doc_str.isdigit() and not doc_str.startswith('000000000'): # Evitar CPF de '0'
            documentos_encontrados.append(doc_str)

    # Remove duplicatas mantendo a ordem de primeira ocorrência
    documentos_unicos = []
    for doc in documentos_encontrados:
        if doc not in documentos_unicos:
            documentos_unicos.append(doc)

    # Atribui o primeiro documento encontrado como prestador e o segundo como tomador
    doc_prestador = None
    doc_tomador = None

    if documentos_unicos:
        doc_prestador = documentos_unicos[0]
        if len(documentos_unicos) > 1:
            doc_tomador = documentos_unicos[1]

    return doc_prestador, doc_tomador