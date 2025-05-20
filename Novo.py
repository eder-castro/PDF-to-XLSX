import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path

def preprocess_image(image_path, filter_type):
    """Pré-processa a imagem com um filtro específico."""
    try:
        img = Image.open(image_path).convert('L') # Converte para escala de cinza
        if filter_type == 'max':
            img = img.filter(ImageFilter.MaxFilter(size=3)) # Aumentar o tamanho do filtro pode ajudar
        elif filter_type == 'median':
            img = img.filter(ImageFilter.MedianFilter(size=3))
        elif filter_type == 'unsharp_mask':
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        elif filter_type == 'sharpen':
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'minfilter':
            img = img.filter(ImageFilter.MinFilter(size=3))
        elif filter_type == 'threshold': # Adicionando um filtro de binarização simples
            img = img.point(lambda x: 0 if x < 128 else 255)
        return img
    except Exception as e:
        print(f"Erro ao pré-processar a imagem com {filter_type}: {e}")
        return None

def extrair_dados_nf(caminho_imagem):
    """Extrai dados relevantes de uma imagem de NF com tentativas de pré-processamento para todos os campos faltantes."""
    try:
        imagem_pil_original = Image.open(caminho_imagem)

        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_nf = extrair_campos(texto_original, os.path.basename(caminho_imagem)) # Passa o nome do arquivo aqui
        #print("***************** ORIGINAL    *****************\n", texto_original)
        
        campos_faltantes = [key for key, value in dados_nf.items() if value is None or value == '']

        if campos_faltantes:
            filtros = ['threshold', 'sharpen', 'max', 'median', 'unsharp_mask', 'minfilter'] 
            for filtro in filtros:
                imagem_pre_processada = preprocess_image(caminho_imagem, filtro)
                if imagem_pre_processada:
                    texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                    dados_nf_pre_processado = extrair_campos(texto_pre_processado, os.path.basename(caminho_imagem))
                    #print("***************** PRE PROCESSADO *****************\n",texto_pre_processado)
                    for campo in campos_faltantes:
                        # Atualiza apenas se o campo ainda estiver faltando e o filtro encontrou algo
                        if (dados_nf[campo] is None or dados_nf[campo] == '') and dados_nf_pre_processado.get(campo) and dados_nf_pre_processado.get(campo) != '':
                            dados_nf[campo] = dados_nf_pre_processado[campo]

        print(dados_nf)
        return dados_nf

    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {e}")
        return {}

def extrair_campos(texto, nome_arquivo):
    """Extrai campos usando REGEX a partir do texto fornecido."""
    dados_nf = {
        "Numero_Nota": None,
        "Data_Emissao": None,
        "CNPJ_Prestador": None,
        "CNPJ_Tomador": None,
        "Pedido": None,
        "Contrato": None,
        "Valor_Total": None,
        "Nome_Arquivo": nome_arquivo # Adiciona o nome do arquivo diretamente aqui
    }

    # Número da Nota - Mais robusto para o exemplo fornecido
    numero_nota_match = re.search(r'(?:NFS-e|Nota Fiscal Eletrônica de Serviço - NFS-e)\s*[\D]*?(\d+)', texto, re.IGNORECASE)
    if numero_nota_match:
        dados_nf["Numero_Nota"] = numero_nota_match.group(1).strip()
    else:
        numero_nota_match = re.search(r'Número da la Feia \[m\]\s*(\d+)', texto) # Para pegar o "313"
        if numero_nota_match:
            dados_nf["Numero_Nota"] = numero_nota_match.group(1).strip()
        else: # Tenta capturar "SÃO PAULO [ \d+ ]"
            numero_nota_match = re.search(r"SÃO PAULO \[\s*(\d+)\s*\]", texto)
            if numero_nota_match:
                dados_nf["Numero_Nota"] = numero_nota_match.group(1).strip()
            else: # Tenta capturar "SÃO PAULO \d+"
                numero_nota_match = re.search(r"SÃO PAULO (\d+)", texto)
                if numero_nota_match:
                    dados_nf["Numero_Nota"] = numero_nota_match.group(1).strip()


    # Data de Emissão
    data_emissao_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    dados_nf["Data_Emissao"] = data_emissao_match.group(1).strip() if data_emissao_match else None

    # Lista de CNPJs
    cnpj_list = re.findall(r"([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}\s?-\s?[\d]{2})", texto)
    if cnpj_list:
        dados_nf["CNPJ_Prestador"] = cnpj_list[0].replace(" ", "")
        if len(cnpj_list) > 1:
            # Tenta encontrar o CNPJ do tomador que não seja igual ao prestador, se houver
            tomador_cnpj_found = False
            for cnpj in cnpj_list[1:]:
                cleaned_cnpj = cnpj.replace(" ", "")
                if cleaned_cnpj != dados_nf["CNPJ_Prestador"]:
                    dados_nf["CNPJ_Tomador"] = cleaned_cnpj
                    tomador_cnpj_found = True
                    break
            if not tomador_cnpj_found:
                dados_nf["CNPJ_Tomador"] = None # Se todos forem iguais ou não houver segundo, define como None
        else:
            dados_nf["CNPJ_Tomador"] = None
    else:
        dados_nf["CNPJ_Prestador"] = None
        dados_nf["CNPJ_Tomador"] = None

    # Pedido e Contrato
    pedidos = ["42000", "43000", "45000"]
    contratos = ["47000", "48000"]

    def buscar_numero_no_texto(texto_completo, termos):
        for termo in termos:
            # Procura por 10 dígitos que começam com um dos termos
            match = re.search(r'\b' + re.escape(termo) + r'\d{5}\b', texto_completo)
            if match:
                return match.group(0) # Retorna a string completa (ex: 4200012345)
            
            # Caso o termo esteja seguido de um espaço e depois os 5 digitos restantes
            match = re.search(r'\b' + re.escape(termo) + r'\s*(\d{5})\b', texto_completo)
            if match:
                return termo + match.group(1) # Retorna a string completa (ex: 4200012345)
        return None

    dados_nf["Pedido"] = buscar_numero_no_texto(texto, pedidos)
    dados_nf["Contrato"] = buscar_numero_no_texto(texto, contratos)

    # Valores
    valor_total = None
    # Prioriza o padrão com "TOTAL DA NOTA =" ou "VALOR TOTAL DA NOTA"
    valor_total_match = re.search(r"(?:TOTAL DA NOTA|VALOR TOTAL DA NOTA) =?\s*R\$?\s*([\d\.,]+)", texto, re.IGNORECASE)
    if valor_total_match:
        valor_total = valor_total_match.group(1).strip()
    else:
        # Tenta padrões comuns para valor total, com mais flexibilidade
        valor_total_match = re.search(r'(?:Valor Total da Nota|TOTAL DO SERVIÇO|VALOR TOTAL RECEBIDO|VALOR TOTAL.*?)\s*R\$?\s*([\d\.]+,\d{2})', texto, re.IGNORECASE)
        if valor_total_match:
            valor_total = valor_total_match.group(1).strip()
        else:
            # Última tentativa para "Valor do Serviço R$ X.XXX,XX"
            valor_total_match = re.search(r'Valor do Serviço R\$?\s*([\d\.]+,\d{2})', texto, re.IGNORECASE)
            if valor_total_match:
                valor_total = valor_total_match.group(1).strip()
    
    dados_nf["Valor_Total"] = valor_total

    return dados_nf

def criar_planilha_excel(dados_nfs, caminho_excel='dados_nfs.xlsx'):
    """Cria uma planilha Excel com os dados das NFs."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Dados das NFs'

    # Cabeçalho
    cabecalho = ['Número NF', 'Data de Emissão', 'CNPJ Fornecedor', 'CNPJ Empresa', 'Contrato', 'Pedido', 'Valor NF', 'Nome do Arquivo']
    sheet.append(cabecalho)

    # Dados
    for nf in dados_nfs:
        linha = [nf.get('Numero_Nota', '-'), nf.get('Data_Emissao', '-'), nf.get('CNPJ_Prestador', '-'),
                 nf.get('CNPJ_Tomador', '-'), nf.get('Contrato', '-'), nf.get('Pedido', '-'),
                 nf.get('Valor_Total', '-'), nf.get('Nome_Arquivo', '-')]
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