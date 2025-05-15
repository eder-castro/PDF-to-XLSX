import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path # Importe a biblioteca pdf2image

def preprocess_image(image_path):
    try:
        img = Image.open(image_path).convert('L') # Abre e converte para escala de cinza
        #img = img.filter(ImageFilter.SHARPEN)
        #img = img.filter(ImageFilter.CONTOUR)
        #img = img.filter(ImageFilter.EDGE_ENHANCE)
        #img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        img = img.filter(ImageFilter.MaxFilter)
        # Adicione outros pré-processamentos conforme necessário (contraste, binarização, etc.)
        return img
    except Exception as e:
        print(f"Erro ao pré-processar a imagem: {e}")
        return None

def extrair_dados_nf(caminho_imagem):
    """Extrai dados relevantes de uma imagem de NF."""
    try:
        imagem_pil = Image.open(caminho_imagem) # Abre a imagem

        # Aplica o pré-processamento
        imagem_pre_processada = preprocess_image(caminho_imagem)
        if imagem_pre_processada:
            texto = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
        else:
            texto = pytesseract.image_to_string(imagem_pil, lang='por')

        print(f"Texto extraído de {caminho_imagem}:\n{texto}")
        dados_nf = {}

        # Número da Nota
        numero_nota = None
        numero_nota_match = re.search(r"SÃO PAULO (\d+)", texto) # SBC
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
        else:
            numero_nota_match = re.search(r"Número da Nota\s*(\d+)", texto) # Cotia
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
            else:
                numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto) # SP
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                else:
                    numero_nota_match = re.search(r",..\s*(\d+)Número da NFS-e", texto) # Floripa
                    if numero_nota_match:
                        numero_nota = numero_nota_match.group(1).strip()
                    else:
                        numero_nota_match = re.search(r'(?:Número:|Nº:|Nota Fiscal:)\s*([^\s]+)', texto) # Novo
                        if numero_nota_match:
                            numero_nota = numero_nota_match.group(1).strip()
                        else:
                            numero_nota = None
        dados_nf["Numero_Nota"] = numero_nota

        # Data de Emissão
        data_emissao_match = re.search(r'(?:Data de Emissão:|Emissão:)\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', texto)
        if data_emissao_match:
            dados_nf['data_emissao'] = data_emissao_match.group(1).strip()
        else:
            dados_nf['data_emissao'] = None

        #Lista de CNPJs
        cnpj_list = re.findall(r'CNPJ:\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
        if cnpj_list:
            dados_nf["CNPJ_do_Prestador"] = cnpj_list[0]
            if len(cnpj_list) > 1:
                dados_nf["CNPJ_do_Tomador"] = cnpj_list[1]
            else:
                dados_nf["CNPJ_do_Tomador"] = None
        else:
            dados_nf["CNPJ_do_Prestador"] = None
            dados_nf["CNPJ_do_Tomador"] = None



        # # CNPJ Prestador
        # cnpj_emitente_match = re.search(r'CNPJ:\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
         # if cnpj_emitente_match:
        #     dados_nf['cnpj_emitente'] = cnpj_emitente_match.group(1)
        # else:
        #     dados_nf['cnpj_emitente'] = None

        # Nome do Prestador
        nome_prestador_match = re.search(r'(?:Nome/Razão Social:|Prestador:|Emitente:)\s*(.+)', texto)
        if nome_prestador_match:
            dados_nf['nome_prestador'] = nome_prestador_match.group(1).strip()
        else:
            dados_nf['nome_prestador'] = None

        # # CNPJ Tomador
        # cnpj_tomador_match = re.search(r'(?:CNPJ do Tomador:|CNPJ Destinatário:)\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
        # if cnpj_tomador_match:
        #     dados_nf['cnpj_tomador'] = cnpj_tomador_match.group(1).strip()
        # else:
        #     dados_nf['cnpj_tomador'] = None

        # Nome do Tomador
        nome_tomador_match = re.search(r'(?:Nome/Razão Social:|Tomador:|Destinatário:)\s*(.+)', texto)
        if nome_tomador_match:
            dados_nf['nome_tomador'] = nome_tomador_match.group(1).strip()
        else:
            dados_nf['nome_tomador'] = None


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
        dados_nf["Pedido"] = num_pedido
        dados_nf["Contrato"] = num_contrato

        # Valor da NF
        valor_total_match = re.search(r'(?:Valor Total:|Valor Total da Nota:)\s*(R\$\s*)?([\d\.]+,\d{2}|\d+,\d{2})', texto)
        if valor_total_match:
            valor_total_str = valor_total_match.group(2).strip().replace('.', '').replace(',', '.') # Remove separador de milhar e troca vírgula por ponto
            try:
                dados_nf['valor_total'] = float(valor_total_str)
            except ValueError:
                dados_nf['valor_total'] = None
        else:
            dados_nf['valor_total'] = None

        # Adicione mais extrações para outros campos...
        print(dados_nf)
        return dados_nf
    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {e}")
        return None

def criar_planilha_excel(dados_nfs, caminho_excel='dados_nfs.xlsx'):
    """Cria uma planilha Excel com os dados das NFs."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Dados das NFs'

    # Cabeçalho
    cabecalho = ['Número NF','Data de Emissão','CNPJ Fornecedor','Fornecedor','CNPJ Empresa','Empresa','Pedido','Contrato','Valor NF']
    sheet.append(cabecalho)

    # Dados
    for nf in dados_nfs:
        linha = [nf.get('numero_nota', '-'),nf.get('data_emissao', '-'),nf.get('cnpj_emitente', '-'),nf.get('nome_prestador', '-'),nf.get('cnpj_tomador', '-'),nf.get('nome_tomador', '-'),nf.get('Pedido','-'),nf.get('Contrato','-'),nf.get('valor_total', '-')]
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