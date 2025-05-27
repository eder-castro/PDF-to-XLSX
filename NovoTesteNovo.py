import pytesseract
from PIL import Image, ImageFilter
import io

# Funções placeholder (substitua pelas suas implementações reais)
# ---INÍCIO CÓDIGO PLACEHOLDER---
def extrair_campos(texto):
    """
    Função placeholder para extrair campos de texto.
    Em um cenário real, esta função conteria a lógica para parsear o texto
    e extrair os dados relevantes, retornando um dicionário.
    Para este exemplo, simula a extração de 'Nome', 'CPF' e 'Valor'.
    """
    dados = {
        "Nome": None,
        "CPF": None,
        "Valor": None
    }

    if "João Silva" in texto:
        dados["Nome"] = "João Silva"
    if "123.456.789-00" in texto:
        dados["CPF"] = "123.456.789-00"
    if "R$ 1500,00" in texto:
        dados["Valor"] = "1500,00"

    return dados

def preprocessamento(arquivo, filtro):
    """
    Função placeholder para aplicar pré-processamento à imagem.
    Em um cenário real, esta função aplicaria o filtro especificado.
    Para este exemplo, ela retorna uma imagem modificada com base no filtro.
    """
    try:
        imagem_pil = Image.open(arquivo).convert('L')
        if filtro == 'max':
            return imagem_pil.filter(ImageFilter.MaxFilter(3))
        elif filtro == 'median':
            return imagem_pil.filter(ImageFilter.MedianFilter(3))
        elif filtro == 'unsharp_mask':
            return imagem_pil.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        elif filtro == 'sharpen':
            return imagem_pil.filter(ImageFilter.SHARPEN)
        elif filtro == 'minfilter':
            return imagem_pil.filter(ImageFilter.MinFilter(3))
        elif filtro == 'smooth':
            return imagem_pil.filter(ImageFilter.SMOOTH)
        elif filtro == 'smooth_more':
            return imagem_pil.filter(ImageFilter.SMOOTH_MORE)
        elif filtro == 'find_edges':
            return imagem_pil.filter(ImageFilter.FIND_EDGES)
        elif filtro == 'emboss':
            return imagem_pil.filter(ImageFilter.EMBOSS)
        elif filtro == 'edge_enhance_more':
            return imagem_pil.filter(ImageFilter.EDGE_ENHANCE_MORE)
        elif filtro == 'edge_enhance':
            return imagem_pil.filter(ImageFilter.EDGE_ENHANCE)
        elif filtro == 'detail':
            return imagem_pil.filter(ImageFilter.DETAIL)
        elif filtro == 'contour':
            return imagem_pil.filter(ImageFilter.CONTOUR)
        elif filtro == 'blur':
            return imagem_pil.filter(ImageFilter.BLUR)
        else:
            return imagem_pil # Retorna a original se o filtro não for reconhecido
    except Exception as e:
        print(f"Erro no pré-processamento com filtro {filtro}: {e}")
        return None

# Variável global (para fins de exemplo)
qt_arquivos_img = 0

# ---FIM CÓDIGO PLACEHOLDER---

def extrair_dados_PDFImagem(arquivo):
    global qt_arquivos_img
    """Extrai dados relevantes de uma imagem de NF com tentativas de pré-processamento para todos os campos faltantes."""
    try:
        qt_arquivos_img += 1
        imagem_pil_original = Image.open(arquivo).convert('L')
        texto_original = pytesseract.image_to_string(imagem_pil_original, lang='por', config='--psm 6 --oem 3')
        dados_extraidos_img = extrair_campos(texto_original)

        filtros = ['max', 'median', 'unsharp_mask', 'sharpen', 'minfilter', 'smooth', 'smooth_more', 'find_edges',
                   'emboss', 'edge_enhance_more', 'edge_enhance', 'detail', 'contour', 'blur']

        # Inicializa a lista de campos faltantes
        campos_faltantes_atual = [key for key, value in dados_extraidos_img.items() if value is None]
        print(f"Campos faltantes iniciais: {campos_faltantes_atual}")

        for filtro in filtros:
            if not campos_faltantes_atual:
                print("Todos os campos faltantes foram preenchidos. Parando loop de filtros.")
                break

            imagem_pre_processada = preprocessamento(arquivo, filtro)
            if imagem_pre_processada:
                print(f"Tentando extrair campos com filtro: {filtro}")
                texto_pre_processado = pytesseract.image_to_string(imagem_pre_processada, lang='por', config='--psm 6 --oem 3')
                dados_nf_pre_processado = extrair_campos(texto_pre_processado)

                # Itera sobre os campos faltantes atuais para tentar preenchê-los
                for campo in list(campos_faltantes_atual): # Itera sobre uma cópia
                    if dados_extraidos_img.get(campo) is None: # Verifica se ainda está faltando no resultado final
                        valor_encontrado_com_filtro = dados_nf_pre_processado.get(campo)
                        if valor_encontrado_com_filtro:
                            dados_extraidos_img[campo] = valor_encontrado_com_filtro
                            # NÃO remove o campo aqui, a lista será recriada mais abaixo.

                # Recalcula campos_faltantes_atual após cada filtro
                # Esta é a mudança chave para garantir que a lista esteja sempre atualizada
                campos_faltantes_atual = [key for key, value in dados_extraidos_img.items() if value is None]
                print(f"Campos faltantes após filtro '{filtro}': {campos_faltantes_atual}")

        print(f"Dados extraídos finais: {dados_extraidos_img}")
        return dados_extraidos_img
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")
        return {}

# --- Exemplo de uso (requer um arquivo de imagem de teste) ---
# Crie uma imagem de teste para simular o processo
from PIL import Image, ImageDraw, ImageFont
import os

def criar_imagem_teste(nome_arquivo, texto_para_simular_ocr, nome_fonte="arial.ttf"):
    try:
        # Tenta usar a fonte Arial
        font = ImageFont.truetype(nome_fonte, 20)
    except IOError:
        # Fallback para uma fonte padrão se Arial não for encontrada
        font = ImageFont.load_default()

    img = Image.new('RGB', (400, 200), color = 'white')
    d = ImageDraw.Draw(img)
    d.text((10,10), texto_para_simular_ocr, fill=(0,0,0), font=font)
    img.save(nome_arquivo)

# Simular um cenário onde o 'Nome' está faltando inicialmente, mas é encontrado com um filtro
arquivo_teste_1 = "teste_nf_1.png"
criar_imagem_teste(arquivo_teste_1, "CPF: 123.456.789-00\nValor: R$ 1500,00")
print("\n--- Teste 1: Nome ausente inicialmente ---")
extrair_dados_PDFImagem(arquivo_teste_1)
os.remove(arquivo_teste_1)

# Simular um cenário onde todos os campos são encontrados no texto original
arquivo_teste_2 = "teste_nf_2.png"
criar_imagem_teste(arquivo_teste_2, "Nome: João Silva\nCPF: 123.456.789-00\nValor: R$ 1500,00")
print("\n--- Teste 2: Todos os campos presentes originalmente ---")
extrair_dados_PDFImagem(arquivo_teste_2)
os.remove(arquivo_teste_2)

# Simular um cenário onde o 'Valor' está ilegível (não encontrado)
arquivo_teste_3 = "teste_nf_3.png"
criar_imagem_teste(arquivo_teste_3, "Nome: João Silva\nCPF: 123.456.789-00") # Sem valor
print("\n--- Teste 3: Valor ausente ---")
extrair_dados_PDFImagem(arquivo_teste_3)
os.remove(arquivo_teste_3)