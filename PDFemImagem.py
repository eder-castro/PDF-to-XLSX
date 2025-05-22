import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path

def preprocess_image(image_path, filter_type):
    """Pré-processa a imagem com um filtro específico."""
    try:
        img = Image.open(image_path).convert('L')
        if filter_type == 'max':
            img = img.filter(ImageFilter.MaxFilter)
        elif filter_type == 'median':
            img = img.filter(ImageFilter.MedianFilter)
        elif filter_type == 'unsharp_mask':
            img = img.filter(ImageFilter.UnsharpMask())
        elif filter_type == 'sharpen':
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'minfilter':
            img = img.filter(ImageFilter.MinFilter)
        # Adicione outros filtros conforme necessário
        return img
    except Exception as e:
        print(f"Erro ao pré-processar a imagem com {filter_type}: {e}")
        return None

def extrair_dados_nf(caminho_imagem):
    """Extrai dados relevantes de uma imagem de NF com tentativas de pré-processamento para todos os campos faltantes."""
    try:
        imagem_pil_original = Image.open(caminho_imagem)

        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_nf = extrair_campos(texto_original)
        #print("*****************    ORIGINAL    *****************\n",texto_original)
        campos_faltantes = [key for key, value in dados_nf.items() if value is None]

        if campos_faltantes:
            filtros = ['max', 'median', 'unsharp_mask', 'sharpen', 'minfilter'] # Adicione mais filtros se desejar
            #print(f"Texto extraído de {caminho_imagem}")
            for filtro in filtros:
                imagem_pre_processada = preprocess_image(caminho_imagem, filtro)
                if imagem_pre_processada:
                    #print(f"Tentando extrair campos faltantes com filtro: {filtro}")
                    texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                    dados_nf_pre_processado = extrair_campos(texto_pre_processado)
                    #print("***************** PRE PROCESSADO *****************\n",texto_pre_processado)
                    for campo in campos_faltantes:
                        if dados_nf[campo] is None and dados_nf_pre_processado.get(campo):
                            dados_nf[campo] = dados_nf_pre_processado[campo]

        # print(f"Texto extraído de {caminho_imagem} (original):\n{texto_original}")
        # print(f"Dados extraídos de {caminho_imagem}:\n{dados_nf}")
        print(dados_nf)
        return dados_nf

    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {e}")
        return {}

def extrair_campos(texto):
    """Extrai campos usando REGEX a partir do texto fornecido."""
    dados_nf = {
        "Numero_Nota": None,
        "Data_Emissao": None,
        "CNPJ_Prestador": None,
        "CNPJ_Tomador": None,
        "Pedido": None,
        "Contrato": None,
        "Valor_Total": None
    }

    # Número da Nota
    numero_nota = None
    numero_nota_match = re.search(r'(?:s:\s?= |Barueri |os\s+qo |no;\s+É |qi |nos\s+O |one\s+|“ Co |O\s+a |O\s+asse |O\s+ses |ana|Ciao:)\s*([^\s]+)', texto, re.DOTALL)
    if numero_nota_match:
        numero_nota = numero_nota_match.group(1).strip()
    else:
        numero_nota_match = re.search(r'SÃO PAULO (\d+)', texto, re.DOTALL)
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
        else:
            numero_nota_match = re.search(r"SÃO PAULO \[\s*(\d+)\s*", texto)
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
            else:
                numero_nota_match = re.search(r'JANEIRO (\d+)', texto, re.DOTALL)
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                else:
                    numero_nota_match = re.search(r'SANTA\s*—\s*(\d+)', texto, re.DOTALL)
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                    else:
                        numero_nota_match = re.search(r'NOTA\s*R PADRE ANCHIETA, 1150 (\d+)', texto, re.DOTALL)
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
                        else:
                            numero_nota = None
    dados_nf["Numero_Nota"] = numero_nota

    # Data de Emissão
    data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    dados_nf["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None

    # #Lista de CNPJs
    # cnpj_list = re.findall(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}\s?-\s?[\d]{2})", texto)
    # #print(cnpj_list)
    # if cnpj_list:
    #     dados_nf["CNPJ_Prestador"] = cnpj_list[0].replace(" ","")
    #     if len(cnpj_list) > 1:
    #         if cnpj_list[1] != cnpj_list[0]:
    #             dados_nf["CNPJ_Tomador"] = cnpj_list[1].replace(" ","")
    #         else:
    #             dados_nf["CNPJ_Tomador"] = cnpj_list[2].replace(" ","")
    #     else:
    #         dados_nf["CNPJ_Tomador"] = None
    # else:
    #     dados_nf["CNPJ_Prestador"] = None
    #     dados_nf["CNPJ_Tomador"] = None


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
                                valor_total_match = re.search(r'VALOR DA NOTA = .*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
                                if valor_total_match:
                                    valor_total = valor_total_match.group(1).strip()
                                else:
                                    valor_total_match = re.search(r'VALOR DOS SERVIÇOS: R\$\s*([\d\.,]+)', texto, re.DOTALL)
                                    if valor_total_match:
                                        valor_total = valor_total_match.group(1).strip()
    dados_nf["Valor_Total"] = valor_total if valor_total_match else None

    # Nome do Arquivo
    dados_nf["Nome_Arquivo"] = arquivo_pdf

    return dados_nf

def criar_planilha_excel(dados_nfs, caminho_excel='dados_nfs.xlsx'):
    """Cria uma planilha Excel com os dados das NFs."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Dados das NFs'

    # Cabeçalho
    cabecalho = ['Número NF','Data de Emissão','CNPJ Fornecedor','CNPJ Empresa','Contrato','Pedido','Valor NF', 'Nome do Arquivo']
    sheet.append(cabecalho)

    # Dados
    for nf in dados_nfs:
        linha = [nf.get('Numero_Nota', '-'),nf.get('Data_Emissao', '-'),nf.get('CNPJ_Prestador', '-'),nf.get('CNPJ_Tomador', '-'),nf.get('Contrato','-'),nf.get('Pedido','-'),nf.get('Valor_Total', '-'), nf.get('Nome_Arquivo', '-')]
        sheet.append(linha)
    try:
        workbook.save(caminho_excel)
        print(f"Planilha '{caminho_excel}' criada com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar a planilha: {e}")

if __name__ == "__main__":
    pasta_nfs = './SP Imagem'
    arquivos_pdf = [f for f in os.listdir(pasta_nfs) if f.lower().endswith('.pdf')]
    dados_extraidos = []

    # Caminho para o executável do Poppler (ajuste se necessário)
    path_to_poppler_binaries = r'C:\Users\eder.castro\AppData\Local\Programs\poppler-24.08.0\Library\bin' # Substitua pelo seu caminho real

    for arquivo_pdf in arquivos_pdf:
        caminho_completo_pdf = os.path.join(pasta_nfs, arquivo_pdf)
        try:
            # Converta o PDF para uma lista de objetos PIL Image
            imagens = convert_from_path(caminho_completo_pdf, poppler_path=path_to_poppler_binaries)

            for i, imagem in enumerate(imagens):
                # Salve cada página como uma imagem temporária
                nome_arquivo_imagem = f'temp_page_{os.path.splitext(arquivo_pdf)[0]}_{i}.png'
                imagem.save(nome_arquivo_imagem, 'PNG')

                # Extraia os dados da imagem
                dados = extrair_dados_nf(nome_arquivo_imagem)
                if dados:
                    dados_extraidos.append(dados)

                # Remova o arquivo temporário
                os.remove(nome_arquivo_imagem)

        except Exception as e:
            print(f"Erro ao processar {caminho_completo_pdf}: {e}")

    if dados_extraidos:
        criar_planilha_excel(dados_extraidos)
    else:
        print("Nenhum dado extraído.")