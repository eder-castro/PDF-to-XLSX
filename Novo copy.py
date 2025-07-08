import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path
import PyPDF2
import Extracao
from datetime import datetime
from dateutil import parser

# Caminho para o executável do Poppler (ajuste se necessário)
path_to_poppler_binaries = r'C:\Users\eder.castro\AppData\Local\Programs\poppler-24.08.0\Library\bin' # Substitua pelo seu caminho real

pasta_PDFs = './PDFs'
processados_selec = 0
processados_img = 0
problema_selec = []
arquivos_para_reprocessar = 0
arquivos_nao_processados = []
dados_extraidos = []
proc_selec = True

def parse_data_emissao(data_str):
    try:
        dt = parser.parse(data_str)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception:
        try:
            return datetime.strptime(data_str, "%d/%m/%Y")
        except Exception:
            print(f"[AVISO] Data inválida ignorada: {data_str}")
            return None

def formatar_valor(chave, valor):
    if chave == "Data_Emissao":
        # Exemplo: formatar para ISO
        return parse_data_emissao(valor) if valor else valor
    elif chave == "Nome_Arquivo":
        return valor
    elif chave == "Valor_Total":
        return float(valor.replace(",", ".")) if isinstance(valor, str) else float(valor)
    else:
        return int(valor) if valor and valor.isdigit() else valor

def extrair_dados_PDFSelecionavel(caminho_arquivo):
    #print("Entrou em extrair_dados_PDFSelecionavel")
    global processados_selec
    global arquivos_para_reprocessar
    with open(caminho_arquivo, "rb") as arquivo_pdf:
        reader = PyPDF2.PdfReader(arquivo_pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or "-"
        texto += texto
        #print("***** TEXTO DO PDF SELEC *****\n", texto)
        dados_extraidos_selec = extrair_campos(texto)
        #print(dados_extraidos_selec)
        campos_faltantes_selec = [key for key, value in dados_extraidos_selec.items() if value is None]
        if len(campos_faltantes_selec) == 5:
            arquivos_nao_processados.append(arquivo)
            arquivos_para_reprocessar += 1
        elif len(campos_faltantes_selec) > 0:
            problema_selec.append(arquivo)
        else:
            dados_extraidos.append(dados_extraidos_selec)
            processados_selec += 1
        # print("processados_selec", processados_selec)
        # print("arquivos_para_reprocessar", arquivos_para_reprocessar)
    return dados_extraidos_selec

def extrair_dados_PDFImagem(arquivo):
    #print("Entrou em extrair_dados_PDFImagem")
    global processados_img
    """Extrai dados relevantes de uma imagem de NF com tentativas de pré-processamento para todos os campos faltantes."""
    try:
        imagem_pil_original = Image.open(arquivo)#.convert('L')
        #print("Chama Imagem para: ", arquivo)
        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_extraidos_img = extrair_campos(texto_original)
        #print(dados_extraidos_img)
        #print("*****************    ORIGINAL    *****************\n",texto_original)
        # Filtros a serem testados
        filtros = ['max','median', 'minfilter', 'unsharp_mask', 'sharpen', 'contour',
                   'emboss','find_edges', 'edge_enhance', 'edge_enhance_more', 'detail', 'blur','smooth','smooth_more']
        campos_faltantes_atual = [key for key, value in dados_extraidos_img.items() if value is None]
        #print(f"Campos faltantes iniciais: {campos_faltantes_atual}")
        # Continuamos o loop de filtros ENQUANTO houver campos faltando
        # e ENQUANTO houver filtros para tentar.
        # Iterar sobre uma cópia da lista de filtros para não modificar durante o loop
        for filtro in filtros:
            # Se não houver mais campos faltantes, podemos parar os filtros completamente
            if not campos_faltantes_atual:
                # print("Todos os campos faltantes foram preenchidos. Parando loop de filtros.")
                break
            imagem_pre_processada = preprocessamento(arquivo, filtro)
            if imagem_pre_processada:
                #print(f"Tentando extrair campos com filtro: {filtro}")
                texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                dados_nf_pre_processado = extrair_campos(texto_pre_processado)
                #print(f"Texto pré-processado com {filtro}:\n{texto_pre_processado}")
                # Criamos uma cópia da lista para iterar e remover itens se necessário
                for campo in list(campos_faltantes_atual): # <--- Itera sobre uma cópia
                    if dados_extraidos_img.get(campo) is None: # Verifica se ainda está faltando no resultado final
                        valor_encontrado_com_filtro = dados_nf_pre_processado.get(campo)
                        if valor_encontrado_com_filtro:
                            dados_extraidos_img[campo] = valor_encontrado_com_filtro
                # Recalcula campos_faltantes_atual após cada filtro
                # Esta é a mudança chave para garantir que a lista esteja sempre atualizada
                campos_faltantes_atual = [key for key, value in dados_extraidos_img.items() if value is None]
                #print(f"Campos faltantes após filtro '{filtro}': {campos_faltantes_atual}")
        #print(dados_extraidos)
        return dados_extraidos_img
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")
        return {}

def extrair_campos(texto):
    #print("Entrou em extrair_campos")
    dados_nf = {
    "Numero_Nota": None,
    "Data_Emissao": None,
    "CNPJ_Prestador": None,
    "CNPJ_Tomador": None,
    "Pedido": None,
    "Contrato": None,
    "Valor_Total": None,
    "Nome_Arquivo": None
    }

    if proc_selec == True:
        dados_nf["Numero_Nota"] = Extracao.extrai_numero_nota_pdf_selecionavel(texto)
    else:
        dados_nf["Numero_Nota"] = Extracao.extrai_numero_nota_pdf_imagem(texto)
    dados_nf["Data_Emissao"] = Extracao.extrai_data_emissao(texto)
    lista_CNPJs = Extracao.extrai_documentos(texto, Extracao.extrai_Cnpjs, Extracao.extrai_Cpfs)
    dados_nf["CNPJ_Prestador"] = lista_CNPJs[0]
    dados_nf["CNPJ_Tomador"] = lista_CNPJs[1]
    lista_pedido_contrato = Extracao.extrai_pedido_e_contrato(texto)
    dados_nf["Pedido"] = lista_pedido_contrato[0]
    dados_nf["Contrato"] = lista_pedido_contrato[1]
    dados_nf["Valor_Total"] = Extracao.extrai_valores(texto)
    dados_nf["Nome_Arquivo"] = nome_arquivo
    #print("Dados extraídos --------------------------------------------------\n", dados_nf)
    #dados_extraidos.append(dados_nf)
    return dados_nf

def preprocessamento(image_path, filter_type):
    #print("Entrou em preprocess imagem")
    try:
        img = Image.open(image_path).convert('L') # Converte para escala de cinza

        if filter_type == 'max':
            # MaxFilter precisa ser instanciado, e geralmente aceita um 'size'
            img = img.filter(ImageFilter.MaxFilter) # Usando size=3 como exemplo
        elif filter_type == 'median':
            # MedianFilter precisa ser instanciado
            img = img.filter(ImageFilter.MedianFilter) # Usando size=3 como exemplo
        elif filter_type == 'unsharp_mask':
            # UnsharpMask está correto, é uma classe que precisa ser instanciada
            img = img.filter(ImageFilter.UnsharpMask())
        elif filter_type == 'sharpen':
            # SHARPEN é uma constante, não precisa de instanciamento
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'minfilter':
            # MinFilter precisa ser instanciado, e geralmente aceita um 'size'
            img = img.filter(ImageFilter.MinFilter) # Usando size=3 como exemplo
        elif filter_type == 'smooth_more':
            img = img.filter(ImageFilter.SMOOTH_MORE)
        elif filter_type == 'blur':
            # BLUR é uma constante
            img = img.filter(ImageFilter.BLUR)
        elif filter_type == 'contour':
            img = img.filter(ImageFilter.CONTOUR)
        elif filter_type == 'detail':
            img = img.filter(ImageFilter.DETAIL)
        elif filter_type == 'edge_enhance':
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'edge_enhance_more':
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        elif filter_type == 'emboss':
            img = img.filter(ImageFilter.EMBOSS)
        elif filter_type == 'find_edges':
            img = img.filter(ImageFilter.FIND_EDGES)
        elif filter_type == 'smooth':
            img = img.filter(ImageFilter.SMOOTH)
        else:
            print(f"Aviso: Filtro '{filter_type}' não reconhecido. A imagem não foi processada.")
            return img # Retorna a imagem original se o filtro não for encontrado

        return img
    except Exception as e:
        print(f"Erro ao pré-processar a imagem com {filter_type}: {e}")
        return None

def executa_PDFImg(arquivo):
        caminho_completo_pdf = os.path.join(caminho_completo_item, arquivo)
        try: # tente converter o pdf em imagem usando o poppler e extrair as informações
            # Converta o PDF para uma lista de objetos PIL Image
            imagens = convert_from_path(caminho_completo_pdf, poppler_path=path_to_poppler_binaries)
            for i, imagem in enumerate(imagens):
                # Salve cada página como uma imagem temporária
                nome_arquivo_imagem = f'temp_page_{os.path.splitext(arquivo)[0]}_{i}.png'
                imagem.save(nome_arquivo_imagem, 'PNG')
                # Extraia os dados da imagem
                dados = extrair_dados_PDFImagem(nome_arquivo_imagem)
                if dados:
                    dados_extraidos.append(dados)
                # Remova o arquivo temporário
                os.remove(nome_arquivo_imagem)
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")
        return dados_extraidos

if __name__ == "__main__":
    # 1. Listar o conteúdo da pasta principal
    itens_na_pasta_principal = os.listdir(pasta_PDFs)
    for item in itens_na_pasta_principal:
        caminho_completo_item = os.path.join(pasta_PDFs, item)
        # 2. Verificar se o item é uma subpasta (de primeiro nível)
        if os.path.isdir(caminho_completo_item):
            nome_subpasta = item
            #print(f"\n--- Entrando na subpasta: {nome_subpasta} ---")
            arquivos_nao_processados = []
            subpastas_contadas = 0
            arquivos_contados = 0
            # 3. Listar o conteúdo DESSA subpasta
            itens_na_subpasta = os.listdir(caminho_completo_item)
            for arquivo in itens_na_subpasta:
                caminho_completo_sub_item = os.path.join(caminho_completo_item, arquivo)
                if os.path.isdir(caminho_completo_sub_item):
                    subpastas_contadas += 1
                else:
                    arquivos_contados += 1
                    print("- - - - - Processando arquivo ", arquivo, " com a função SELEC - - - - -")
                    proc_selec = True
                    nome_arquivo = arquivo
                    if not extrair_dados_PDFSelecionavel(caminho_completo_sub_item):
                        print("Nenhum arquivo Selec")
            #print(f"Total de pastas em {nome_subpasta} = {subpastas_contadas}")
            # Após tentar processar todos os arquivos da pasta com a função principal,
            # itera sobre os que não foram processados para a função secundária.
            print(f"\n--- Total de arquivos processados pelo Selec = {processados_selec} ---")
            if arquivos_nao_processados:
                print(f"\n--- Reprocessando {arquivos_para_reprocessar} arquivos em {nome_subpasta} que não foram processados inicialmente ---")
                for arquivo_reprocessar in arquivos_nao_processados:
                    print("- - - - - Reprocessando arquivo ", arquivo_reprocessar, "com a função IMG - - - - -")
                    proc_selec = False
                    processados_img += 1
                    nome_arquivo = arquivo_reprocessar
                    executa_PDFImg(arquivo_reprocessar)
            # else:
            #     print(f"\nTodos os arquivos em {nome_subpasta} foram processados pela função PDF_selec.")
            # print(f"--- Saindo da subpasta: {nome_subpasta} ---")
            arquivos_para_reprocessar = 0
            arquivos_nao_processados.clear()
    print("\n- - - - - - - - - - - - - - - - - - DADOS  EXTRAÍDOS - - - - - - - - - - - - - - - - - -")
    for item in dados_extraidos:
        print(item)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
    print(f"Total de arquivos processados pelo Selec = {processados_selec}")
    print(f"Total de arquivos processados pelo Img = {processados_img}")
    print(f"TOTAL DE {processados_selec + processados_img} ARQUIVOS PROCESSADOS...")
    print(problema_selec)