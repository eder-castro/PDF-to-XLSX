import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path
import PyPDF2
import Extracao

# Caminho para o executável do Poppler (ajuste se necessário)
path_to_poppler_binaries = r'C:\Users\eder.castro\AppData\Local\Programs\poppler-24.08.0\Library\bin' # Substitua pelo seu caminho real

pasta_PDFs = './PDFs'
qt_arquivos_selec = 0
qt_arquivos_img = 0
nao_processados = 0
qt_arquivos = 0
dados_extraidos = []

def extrair_dados_PDFSelecionavel(nome_arquivo):
    #print("Entrou em extrair_dados_PDFSelecionavel")
    global qt_arquivos_selec
    global nao_processados
    with open(f"{pasta_e_subpasta_nfs}/{arquivo}", "rb") as arquivo_pdf:
        reader = PyPDF2.PdfReader(arquivo_pdf)
        #print(reader)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or "-"
            #print("***** TEXTO DO PDF *****\n", texto)
            dados_extraidos_selec = extrair_campos(texto)
            #print(dados_extraidos_selec)
            campos_faltantes = [key for key, value in dados_extraidos_selec.items() if value is None]
            if len(campos_faltantes) > 0:
                nao_processados += 1
                print(nao_processados, "-", subpasta)
                #print(dados_extraidos)
                print("Faltantes-----", campos_faltantes)
            else:
                qt_arquivos_selec += 1
            return dados_extraidos_selec
        
def extrair_dados_PDFImagem(arquivo):
    #print("Entrou em extrair_dados_PDFImagem")
    global qt_arquivos_img
    """Extrai dados relevantes de uma imagem de NF com tentativas de pré-processamento para todos os campos faltantes."""
    try:
        qt_arquivos_img +=1
        imagem_pil_original = Image.open(arquivo).convert('L')
        #print("Chama Imagem para: ", arquivo)
        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_extraidos_img = extrair_campos(texto_original)
        #print("*****************    ORIGINAL    *****************\n",texto_original)
        # Filtros a serem testados
        filtros = ['max', 'median', 'unsharp_mask', 'sharpen', 'minfilter', 'smooth', 'smooth_more', 'find_edges',
                   'emboss', 'edge_enhance_more', 'edge_enhance', 'detail', 'contour', 'blur']

        campos_faltantes_atual = [key for key, value in dados_extraidos_img.items() if value is None]
        print(campos_faltantes_atual)
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
                print(f"Tentando extrair campos com filtro: {filtro}")
                texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                dados_nf_pre_processado = extrair_campos(texto_pre_processado)
                #print(f"Texto pré-processado com {filtro}:\n{texto_pre_processado}")
                # Criamos uma cópia da lista para iterar e remover itens se necessário
                for campo in list(campos_faltantes_atual): # <--- Itera sobre uma cópia
                    if dados_extraidos_img.get(campo) is None: # Verifica se ainda está faltando no resultado final
                        valor_encontrado_com_filtro = dados_nf_pre_processado.get(campo)
                        if valor_encontrado_com_filtro:
                            dados_extraidos_img[campo] = valor_encontrado_com_filtro
                            campos_faltantes_atual.remove(campo) # Remove o campo da lista de faltantes
                print("Atual", campos_faltantes_atual)
        #print(f"Texto extraído de {arquivo} (original):\n{texto_original}")
        #print(f"Dados extraídos de {arquivo}:\n{dados_nf}")
        print(dados_extraidos_img)
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
    "Valor_Total": None
    }
    if nao_processados == 0:
        dados_nf["Numero_Nota"] = Extracao.extrai_numero_nota_pdf_selecionavel(texto)
    else:
        dados_nf["Numero_Nota"] = Extracao.extrai_numero_nota_pdf_imagem(texto)
    dados_nf["Data_Emissao"] = Extracao.extrai_data_emissao(texto)
    lista_CNPJs = Extracao.extrai_Cnpjs(texto)
    dados_nf["CNPJ_Prestador"] = lista_CNPJs[0]
    dados_nf["CNPJ_Tomador"] = lista_CNPJs[1]
    lista_pedido_contrato = Extracao.extrai_pedido_e_contrato(texto)
    dados_nf["Pedido"] = lista_pedido_contrato[0]
    dados_nf["Contrato"] = lista_pedido_contrato[1]
    dados_nf["Valor_Total"] = Extracao.extrai_valores(texto)
    return dados_nf

def preprocessamento(image_path, filter_type):
    #print("Entrou em preprocess imagem")
    try:
        img = Image.open(image_path).convert('L') # Converte para escala de cinza

        if filter_type == 'max':
            # MaxFilter precisa ser instanciado, e geralmente aceita um 'size'
            img = img.filter(ImageFilter.MaxFilter(size=3)) # Usando size=3 como exemplo
        elif filter_type == 'median':
            # MedianFilter precisa ser instanciado
            img = img.filter(ImageFilter.MedianFilter(size=3)) # Usando size=3 como exemplo
        elif filter_type == 'unsharp_mask':
            # UnsharpMask está correto, é uma classe que precisa ser instanciada
            img = img.filter(ImageFilter.UnsharpMask())
        elif filter_type == 'smooth_more':
            img = img.filter(ImageFilter.SMOOTH_MORE)
        elif filter_type == 'sharpen':
            # SHARPEN é uma constante, não precisa de instanciamento
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'minfilter':
            # MinFilter precisa ser instanciado, e geralmente aceita um 'size'
            img = img.filter(ImageFilter.MinFilter(size=3)) # Usando size=3 como exemplo
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
        caminho_completo_pdf = os.path.join(pasta_e_subpasta_nfs, arquivo)
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

def executa_PDFSelec(arquivo):
    global qt_arquivos
    qt_arquivos += 1
    dados_retornados_PDFSelecionavel = extrair_dados_PDFSelecionavel(arquivo)
    return dados_retornados_PDFSelecionavel


if __name__ == "__main__":
    for subpasta in os.listdir(pasta_PDFs):
        pasta_e_subpasta_nfs = os.path.join(pasta_PDFs, subpasta)
        lista_arquivos = os.listdir(pasta_e_subpasta_nfs)
        arq_lidos = len(lista_arquivos)
        #print (subpasta)
        #print ("Arquivos na lista: ",len(lista_arquivos))
        # Para cada arquivo na lista de arquivos
        for arquivo in lista_arquivos:
            #subpasta_arquivo = os.path.join(subpasta, arquivo)
            #print(arquivo)
            arq_lidos -= 1
            if arquivo.lower().endswith(".pdf"):
                #print("Chama selecionavel para: ", arquivo)
                dados_retornados_PDFSelec = executa_PDFSelec(arquivo)
                #print (dados_retornados_PDFSelec)
                #print ("Arquivos lidos: ", arq_lidos)
                if nao_processados == 0:
                    print (dados_retornados_PDFSelec)
                else:
                    dados_retornados_PDFImg = executa_PDFImg(arquivo)
                    nao_processados -= 1


print(qt_arquivos_selec, " arquivos --selec-- processados...")
print(qt_arquivos_img, " arquivos --img-- processados...")
print("Total de ",qt_arquivos_img+qt_arquivos_selec, " arquivos processados...")
print("Total de ",qt_arquivos, " arquivos na pasta.")