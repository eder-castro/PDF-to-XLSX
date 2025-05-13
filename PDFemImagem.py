import pytesseract
from PIL import Image
import re
import openpyxl
import os

def extrair_dados_nf(caminho_imagem):
    """Extrai dados relevantes de uma imagem de NF."""
    try:
        texto = pytesseract.image_to_string(Image.open(caminho_imagem), lang='por') # Assumindo português
        dados_nf = {}

        # Exemplo de extração (adapte às suas NFs)
        cnpj_emitente_match = re.search(r'CNPJ:\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
        if cnpj_emitente_match:
            dados_nf['cnpj_emitente'] = cnpj_emitente_match.group(1)

        valor_total_match = re.search(r'Valor Total\s*(R\$\s*[\d,.]+)', texto)
        if valor_total_match:
            dados_nf['valor_total'] = valor_total_match.group(1)

        # Adicione mais extrações para outros campos...

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
    cabecalho = ['CNPJ Emitente', 'Valor Total', '...'] # Adapte ao seus campos
    sheet.append(cabecalho)

    # Dados
    for nf in dados_nfs:
        linha = [nf.get('cnpj_emitente', ''), nf.get('valor_total', ''), '...'] # Adapte
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

    for arquivo_pdf in arquivos_pdf:
        caminho_completo = os.path.join(pasta_nfs, arquivo_pdf)
        # Aqui você precisará converter o PDF para imagem (se necessário)
        # Uma biblioteca como 'pdf2image' pode ajudar:
        # from pdf2image import convert_from_path
        # imagens = convert_from_path(caminho_completo)
        # for i, imagem in enumerate(imagens):
        #     dados = extrair_dados_nf(f'temp_page_{i}.png')
        #     if dados:
        #         dados_extraidos.append(dados)
        #         os.remove(f'temp_page_{i}.png') # Limpar arquivos temporários

        # Para simplificar o exemplo, vamos assumir que você já tem imagens das NFs
        # e que cada PDF tem apenas uma página ou você já as separou.
        # Adapte esta parte conforme a sua necessidade.
        # Exemplo assumindo que o nome do arquivo PDF é o mesmo da imagem (sem extensão)
        nome_base = os.path.splitext(arquivo_pdf)[0]
        caminho_imagem = os.path.join(pasta_nfs, f'{nome_base}.pdf') # Adapte a extensão se necessário
        if os.path.exists(caminho_imagem):
            dados = extrair_dados_nf(caminho_imagem)
            if dados:
                dados_extraidos.append(dados)
        else:
            print(f"Imagem correspondente não encontrada para {arquivo_pdf}")

    if dados_extraidos:
        criar_planilha_excel(dados_extraidos)
    else:
        print("Nenhum dado extraído.")