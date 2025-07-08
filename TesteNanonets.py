import os

# Definir a variável de ambiente para desabilitar a verificação SSL de maneira mais "amigável"
# Outras variáveis como REQUESTS_CA_BUNDLE=false ou CURLOPT_SSL_VERIFYPEER=0 também podem ser usadas,
# mas esta é mais específica para o Hugging Face Hub.
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['CURL_CA_BUNDLE'] = '' # Tentar também limpar o bundle de CA do curl

from transformers import pipeline, AutoProcessor, AutoModelForVision2Seq # Importar AutoProcessor e AutoModelForVision2Seq
#import requests
from PIL import Image
#from io import BytesIO
from pdf2image import convert_from_path

# Caminho para o executável do Poppler (ajuste se necessário)
path_to_poppler_binaries = r'C:\Users\eder.castro\AppData\Local\Programs\poppler-24.08.0\Library\bin' # Substitua pelo seu caminho real

pasta_PDFs = './PDFs'
itens_na_pasta_principal = os.listdir(pasta_PDFs)
for item in itens_na_pasta_principal:
    nome_arquivo = item

def converteImagem(arquivo):
    caminho_completo_pdf = os.path.join(pasta_PDFs, arquivo)
    print(caminho_completo_pdf)
    try: # tente converter o pdf em imagem usando o poppler e extrair as informações
        # Converta o PDF para uma lista de objetos PIL Image
        imagens = convert_from_path(caminho_completo_pdf, poppler_path=path_to_poppler_binaries, dpi=600)
        for i, imagem in enumerate(imagens):
            # Salve cada página como uma imagem temporária
            nome_arquivo_imagem = f'temp_page_{os.path.splitext(arquivo)[0]}_{i}.png'
            imagem.save(nome_arquivo_imagem, 'PNG')
            # Extraia os dados da imagem
            print()
            return nome_arquivo_imagem
            #os.remove(nome_arquivo_imagem)
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")
        return imagem

imagem = converteImagem(nome_arquivo)

# Carregar o modelo Nanonets-OCR
try:
    print("Carregando processador...")
    processor = AutoProcessor.from_pretrained("nanonets/Nanonets-OCR-s")
    if processor is None:
        raise ValueError("AutoProcessor retornou None. Verifique instalação e conexão.")
    print("Processador carregado com sucesso!")

    print("Carregando modelo...")
    model = AutoModelForVision2Seq.from_pretrained("nanonets/Nanonets-OCR-s")
    if model is None:
        raise ValueError("AutoModelForVision2Seq retornou None. Verifique instalação, conexão e recursos.")
    print("Modelo carregado com sucesso!")
    
    # Carregar a imagem local
    if not os.path.exists(imagem):
        raise FileNotFoundError(f"Arquivo de imagem não encontrado no caminho: {imagem}")
    image = Image.open(imagem).convert("RGB") # Converter para RGB é crucial
    print(f"Imagem '{imagem}' carregada com sucesso!")
    
    # Processa a imagem para gerar as entradas que o modelo espera
    # O processor irá gerar 'pixel_values' e também 'input_ids' (que ele espera mesmo para imagens)
    # se a arquitetura do modelo exigir, ou passará um valor padrão adequado.
    inputs = processor(images=image, return_tensors="pt") # Retorna tensores PyTorch
    
    print("Executando inferência do modelo...")
    # Realiza a geração de texto.
    # Usamos 'pixel_values' que vêm do processamento da imagem.
    # O 'max_length' define o comprimento máximo do texto gerado.
    generated_ids = model.generate(pixel_values=inputs.pixel_values, max_length=1024)
    
    # Decodifica os IDs gerados de volta para texto legível
    extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
    
    # O resultado será uma lista, pegue o primeiro elemento
    if extracted_text:
        text_result = extracted_text[0]
        print("\n--- Texto Extraído ---")
        print(text_result)
    else:
        print("Nenhum texto foi extraído da imagem.")
        
except FileNotFoundError as e:
    print(f"Erro: {e}")
    print("Verifique se o nome do arquivo e o caminho estão corretos, e se o arquivo está na mesma pasta do script ou no caminho absoluto.")
except Exception as e:
    print(f"Erro geral durante o carregamento ou inferência do modelo: {e}")
    print("Verifique novamente sua conexão, as instalações das bibliotecas, e se há problemas de proxy/SSL persistentes.")

# # 2. Carregar a imagem da Nota Fiscal
# # Você pode carregar a imagem de um arquivo local ou de uma URL.
# # Para este exemplo, vamos usar uma imagem de exemplo de uma URL.
# # Substitua esta URL pelo caminho do seu arquivo de imagem local se preferir.
# #image_url = "https://www.fiscaliza-net.com.br/wp-content/uploads/2019/08/Exemplo-Nota-Fiscal-Eletronica-e-PDF-de-Dacte.jpg"

# try:    
#     image = Image.open(imagem).convert("RGB") # Garante que a imagem está em RGB
#     print("Imagem carregada com sucesso!")
# except FileNotFoundError as e:
#     print(f"Erro: {e}")
#     print("Verifique se o nome do arquivo e o caminho estão corretos, e se o arquivo está na mesma pasta do script ou no caminho absoluto.")
#     exit()
# except Exception as e:
#     print(f"Erro ao carregar a imagem: {e}")
#     print("Pode ser que o arquivo esteja corrompido ou em um formato inválido.")
#     exit()


# # 3. Executar o OCR na imagem
# print("Extraindo texto da imagem...")
# extracted_text = ocr_pipeline(image)

# # O resultado pode ser uma lista de dicionários.
# # Para o Nanonets-OCR, o texto geralmente estará na chave 'text'.
# if extracted_text and isinstance(extracted_text, list) and len(extracted_text) > 0:
#     text_result = extracted_text[0].get('generated_text', '') # Alguns pipelines podem usar 'generated_text'
#     if not text_result: # Se 'generated_text' não estiver presente, tente 'text'
#         text_result = extracted_text[0].get('text', '')
#     print("\n--- Texto Extraído ---")
#     print(text_result)
# else:
#     print("Nenhum texto foi extraído da imagem.")

# # 4. Processar o texto extraído para sua planilha Excel
# # Aqui é onde a "mágica" acontece para o seu app.
# # Você precisará de lógica para identificar os campos específicos (CNPJ, Valor, Data, etc.)
# # no texto extraído e depois salvá-los em sua planilha Excel usando bibliotecas como 'pandas' ou 'openpyxl'.

print("\n--- Próximos Passos ---")
print("Agora, você precisará adicionar lógica para:")
print("1. Salvar as imagens de NFs localmente (se ainda não o faz).")
print("2. Iterar sobre as NFs e aplicar o OCR.")
print("3. Usar Expressões Regulares (Regex) ou outras técnicas de processamento de texto para extrair informações como CNPJ, valor, data, etc. (isso pode ser o mais desafiador).")
print("4. Armazenar os dados extraídos em uma estrutura (como um dicionário ou lista de dicionários).")
print("5. Exportar esses dados para uma planilha Excel usando bibliotecas como 'pandas' (DataFrame.to_excel()) ou 'openpyxl'.")