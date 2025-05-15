import pytesseract
from PIL import Image, ImageFilter
import re
import openpyxl
import os
from pdf2image import convert_from_path # Importe a biblioteca pdf2image

def preprocess_image(image_path):
    try:
        img = Image.open(image_path).convert('L')
        img = img.filter(ImageFilter.MaxFilter)
        return img
    except Exception as e:
        print(f"Erro ao pré-processar a imagem: {e}")
        return None

def extrair_dados_nf(caminho_imagem):
    """Extrai dados relevantes de uma imagem de NF."""
    try:
        imagem_pil_original = Image.open(caminho_imagem)
        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_nf = extrair_campos(texto_original)

        if not any(value for value in dados_nf.values() if value):
            imagem_pre_processada = preprocess_image(caminho_imagem)
            if imagem_pre_processada:
                texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                dados_nf_pre_processado = extrair_campos(texto_pre_processado)
                for key, value in dados_nf_pre_processado.items():
                    if value:
                        dados_nf[key] = value

        # print(f"Texto extraído de {caminho_imagem} (original):\n{texto_original}")
        # if 'texto_pre_processado' in locals():
        #     print(f"Texto extraído de {caminho_imagem} (pré-processado):\n{texto_pre_processado}")
        # print(f"Dados extraídos de {caminho_imagem}:\n{dados_nf}")

        return dados_nf

    except Exception as e:
        print(f"Erro ao processar {caminho_imagem}: {e}")
        return {}
    
def extrair_campos(texto):
    """Extrai campos usando REGEX a partir do texto fornecido."""
    dados_nf = {}

    # Número da Nota
    numero_nota = None
    numero_nota_match = re.search(r"Número da Nota\s+(\d+)", texto) # Padrão para "Número da Nota  00007060"
    if numero_nota_match:
        numero_nota = numero_nota_match.group(1).strip()
    else:
        numero_nota_match = re.search(r"Competência(\d+)", texto) # SBC
        if numero_nota_match:
            numero_nota = numero_nota_match.group(1).strip()
        else:
            numero_nota_match = re.search(r"Nota:\s*(\d+)", texto) # Cotia
            if numero_nota_match:
                numero_nota = numero_nota_match.group(1).strip()
            else:
                numero_nota_match = re.search(r"R\$\s*0,00(\d+)", texto) # SP
                if numero_nota_match:
                    numero_nota = numero_nota_match.group(1).strip()
                else:
                    numero_nfse_match = re.search(r",..\s*(\d+)Número da NFS-e", texto) # Floripa
                    if numero_nfse_match:
                        numero_nota = numero_nfse_match.group(1).strip()
                    # Não precisa de 'else: numero_nota = None' aqui, pois já foi inicializado

    dados_nf["Numero_Nota"] = numero_nota

    # Data de Emissão
    data_emissao_match = re.search(r'(?:Data de Emissão:|Emissão:)\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', texto)
    if data_emissao_match:
        dados_nf['data_emissao'] = data_emissao_match.group(1).strip()

    # Lista de CNPJs
    cnpj_prestador = None
    cnpj_prestador_match = re.search(r'PRESTADOR DE SERVIÇOS.*?\b(\d{2}\s*\.?\s*\d{3}\s*\.?\s*\d{3}[/\s-]?\s*\d{4}-?\s*\d{2})\b', texto, re.DOTALL)
    if cnpj_prestador_match:
        cnpj_prestador = "".join(filter(str.isdigit, cnpj_prestador_match.group(1)))
    dados_nf["CNPJ_Prestador"] = cnpj_prestador

    cnpj_tomador = None
    cnpj_tomador_match = re.search(r'TOMADOR DE SERVIÇOS.*?\b(\d{2}\s*\.?\s*\d{3}\s*\.?\s*\d{3}[/\s-]?\s*\d{4}-?\s*\d{2})\b', texto, re.DOTALL)
    if cnpj_tomador_match:
        cnpj_tomador = "".join(filter(str.isdigit, cnpj_tomador_match.group(1)))
    else:
        cnpj_tomador_match_alt = re.search(r'TOMADOR DE SERVIÇOS.*?\b(\d{14})\b', texto.replace(" ", ""), re.DOTALL)
        if cnpj_tomador_match_alt:
            cnpj_tomador = cnpj_tomador_match_alt.group(1)
    dados_nf["CNPJ_Tomador"] = cnpj_tomador

    # Pedido e Contrato (mantive como estava)
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
        # elif isinstance(item_na_descricao, list):
        #     # ... (restante da lógica para listas e dicionários) ...
        #     pass # Adicione a lógica completa se necessário
        # elif isinstance(item_na_descricao, dict):
        #     # ... (restante da lógica para dicionários) ...
        #     pass # Adicione a lógica completa se necessário
    dados_nf["Pedido"] = num_pedido
    dados_nf["Contrato"] = num_contrato

    # Valor da NF
    valor_total = None

    # Tenta pegar o VALOR TOTAL RECEBIDO primeiro
    valor_recebido_match = re.search(r'[Vv]ALOR TOTAL RECEBIDO.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
    if valor_recebido_match:
        valor_total_str = valor_recebido_match.group(1).strip().replace('.', '').replace(',', '.')
        try:
            valor_total = float(valor_total_str)
        except ValueError:
            pass  # Mantém valor_total como None em caso de erro de conversão
    else:
        # Se VALOR TOTAL RECEBIDO não for encontrado, tenta pegar o valor após VALOR TOTAL até R$
        valor_total_match = re.search(r'[Vv]ALOR TOTAL.*?R\$[ ]*([\d\.]+,\d{2}|\d+,\d{2})', texto)
        if valor_total_match:
            valor_total_str = valor_total_match.group(1).strip().replace('.', '').replace(',', '.')
            try:
                valor_total = float(valor_total_str)
            except ValueError:
                pass  # Mantém valor_total como None em caso de erro de conversão

    dados_nf['valor_total'] = valor_total
    
    print(dados_nf)
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
        linha = [nf.get('Numero_Nota', '-'),nf.get('data_emissao', '-'),nf.get('CNPJ_Prestador', '-'),nf.get('CNPJ_Tomador', '-'),nf.get('Contrato','-'),nf.get('Pedido','-'),nf.get('valor_total', '-')]
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