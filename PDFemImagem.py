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

def extrair_campo(imagem_pil, regex):
    """Extrai um campo específico usando regex de uma imagem PIL."""
    texto = pytesseract.image_to_string(imagem_pil, lang='por', config='--psm 6 --oem 3')
    match = re.search(regex, texto)
    return match.group(1).strip() if match else None

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
                            #print(f"Campo '{campo}' encontrado com sucesso após pré-processamento com '{filtro}'.")

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
        "valor_total": None
    }

    # Número da Nota
    numero_nota = None
    numero_nota_match = re.search(r"SÃO PAULO (\d+)", texto) # 4992069, 210, 211, 1634, 13788, 86746, 25269, AAKCID, São Paulo
    if numero_nota_match:
        numero_nota = numero_nota_match.group(1).strip()
    else:
        numero_nota_match = re.search(r"SÃO PAULO \[\s*(\d+)\s*", texto)
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
        else:
            numero_nota_match = re.search(r'(?:Número:|Nº:|s:\s?= |qi |Nota Fiscal:|osn-|ans|Ciao:| ne)\s*([^\s]+)', texto, re.DOTALL) # 158707, 303910, 303911, 158706, 10792, 10802, 40839
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
            else:
                numero_nota = None
    dados_nf["Numero_Nota"] = numero_nota

        # numero_nota_match = re.search(r"Número da Nota\s*(\d+)", texto) # Cotia
        # if numero_nota_match:
        #     numero_nota = numero_nota_match.group(1).strip()
        # else:
    # numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto) # SP
    # if numero_nota_match:
    #     numero_nota = numero_nota_match.group(1).strip()
    #         else:
    # numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", texto) # Floripa
    # if numero_nota_match:
    #     numero_nota = numero_nota_match.group(1).strip()
    #             else:
    

    # Data de Emissão
    data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    dados_nf["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None

    # CNPJ Prestador
    cnpj_prestador_match = re.search(r'PRESTADOR DE SERVIÇOS.*?\b(\d{2}\s*\.?\s*\d{3}\s*\.?\s*\d{3}[/\s-]?\s*\d{4}-?\s*\d{2})\b', texto, re.DOTALL)
    if cnpj_prestador_match:
        dados_nf["CNPJ_Prestador"] = "".join(filter(str.isdigit, cnpj_prestador_match.group(1)))

    # CNPJ Tomador
    cnpj_tomador_match = re.search(r'TOMADOR DE SERVIÇOS.*?\b(\d{2}\s*\.?\s*\d{3}\s*\.?\s*\d{3}[/\s-]?\s*\d{4}-?\s*\d{2})\b', texto, re.DOTALL)
    if cnpj_tomador_match:
        dados_nf["CNPJ_Tomador"] = "".join(filter(str.isdigit, cnpj_tomador_match.group(1)))
    else:
        cnpj_tomador_match_alt = re.search(r'TOMADOR DE SERVIÇOS.*?\b(\d{14})\b', texto.replace(" ", ""), re.DOTALL)
        if cnpj_tomador_match_alt:
            dados_nf["CNPJ_Tomador"] = cnpj_tomador_match_alt.group(1)

    # Pedido e Contrato
    descricao = [texto]
    pedidos = ["42000", "43000", "45000"]
    contratos = ["47000", "48000"]
    num_pedido = None
    num_contrato = None
    for item_na_descricao in descricao:
        if isinstance(item_na_descricao, str):
            for pedido in pedidos:
                for palavra in item_na_descricao.split():
                    if pedido in palavra:
                        potential_pedido = palavra[palavra.find(pedido):palavra.find(pedido)+10]
                        if len(potential_pedido) == 10 and potential_pedido.isdigit(): # Verifica o comprimento e se é numérico
                            num_pedido = potential_pedido
                            break # Se encontrou um pedido válido, pode sair do loop de palavras
                if num_pedido: # Se encontrou um pedido válido, pode sair do loop de pedidos
                    break
            for contrato in contratos:
                for palavra in item_na_descricao.split():
                    if contrato in palavra:
                        potential_contrato = palavra[palavra.find(contrato):palavra.find(contrato)+10]
                        if len(potential_contrato) == 10 and potential_contrato.isdigit(): # Verifica o comprimento e se é numérico
                            num_contrato = potential_contrato
                            break # Se encontrou um contrato válido, pode sair do loop de palavras
                if num_contrato: # Se encontrou um contrato válido, pode sair do loop de contratos
                    break
        elif isinstance(item_na_descricao, list):
            for item_da_lista in item_na_descricao:
                if isinstance(item_da_lista, str):
                    for pedido in pedidos:
                        if pedido in item_da_lista:
                            potential_pedido = item_da_lista.strip()
                            if len(potential_pedido) == 10 and potential_pedido.isdigit():
                                num_pedido = potential_pedido
                                break
                    if num_pedido:
                        break
                    for contrato in contratos:
                        if contrato in item_da_lista:
                            potential_contrato = item_da_lista.strip()
                            if len(potential_contrato) == 10 and potential_contrato.isdigit():
                                num_contrato = potential_contrato
                                break
                    if num_contrato:
                        break
                elif isinstance(item_da_lista, dict):
                    for vlr in item_da_lista.values():
                        if isinstance(vlr, str):
                            for pedido in pedidos:
                                if pedido in vlr:
                                    potential_pedido = vlr.strip()
                                    if len(potential_pedido) == 10 and potential_pedido.isdigit():
                                        num_pedido = potential_pedido
                                        break
                            if num_pedido:
                                break
                            for contrato in contratos:
                                if contrato in vlr:
                                    potential_contrato = vlr.strip()
                                    if len(potential_contrato) == 10 and potential_contrato.isdigit():
                                        num_contrato = potential_contrato
                                        break
                            if num_contrato:
                                break
                if num_pedido and num_contrato: # Se ambos foram encontrados, pode sair
                    break
    if num_pedido == None:
        dados_nf["Pedido"] = ''
    else:    
        dados_nf["Pedido"] = num_pedido
    if num_contrato == None:
        dados_nf["Contrato"] = ''
    else:
        dados_nf["Contrato"] = num_contrato

    # Valor da NF
    valor_total = None
    valor_recebido_match = re.search(r'[Vv]ALOR TOTAL RECEBIDO.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
    if valor_recebido_match:
        try:
            valor_total = float(valor_recebido_match.group(1).strip().replace('.', '').replace(',', '.'))
        except ValueError:
            pass
    else:
        valor_total_match = re.search(r'[Vv]ALOR TOTAL.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
        if valor_total_match:
            try:
                valor_total = float(valor_total_match.group(1).strip().replace('.', '').replace(',', '.'))
            except ValueError:
                pass
    dados_nf['valor_total'] = valor_total

    return dados_nf

def criar_planilha_excel(dados_nfs, caminho_excel='dados_nfs.xlsx'):
    """Cria uma planilha Excel com os dados das NFs."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Dados das NFs'

    # Cabeçalho
    cabecalho = ['Número NF','Data de Emissão','CNPJ Fornecedor','CNPJ Empresa','Contrato','Pedido','Valor NF']
    sheet.append(cabecalho)

    # Dados
    for nf in dados_nfs:
        linha = [nf.get('Numero_Nota', '-'),nf.get('Data_Emissao', '-'),nf.get('CNPJ_Prestador', '-'),nf.get('CNPJ_Tomador', '-'),nf.get('Contrato','-'),nf.get('Pedido','-'),nf.get('valor_total', '-')]
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