from transformers import pipeline
import requests
from PIL import Image
from io import BytesIO

# 1. Carregar o modelo Nanonets-OCR
# O 'pipeline' simplifica o uso de modelos pré-treinados para tarefas comuns.
# 'nanonets/Nanonets-OCR-s' é o identificador do modelo no Hugging Face.
try:
    ocr_pipeline = pipeline("image-to-text", model="nanonets/Nanonets-OCR-s")
    print("Modelo Nanonets-OCR carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    print("Verifique sua conexão com a internet e se as bibliotecas estão instaladas corretamente.")
    exit()

# 2. Carregar a imagem da Nota Fiscal
# Você pode carregar a imagem de um arquivo local ou de uma URL.
# Para este exemplo, vamos usar uma imagem de exemplo de uma URL.
# Substitua esta URL pelo caminho do seu arquivo de imagem local se preferir.
image_url = "https://www.fiscaliza-net.com.br/wp-content/uploads/2019/08/Exemplo-Nota-Fiscal-Eletronica-e-PDF-de-Dacte.jpg"

try:
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB") # Garante que a imagem está em RGB
    print("Imagem carregada com sucesso!")
except Exception as e:
    print(f"Erro ao carregar a imagem: {e}")
    print("Certifique-se de que a URL da imagem está correta ou que o caminho do arquivo local existe.")
    exit()

# 3. Executar o OCR na imagem
print("Extraindo texto da imagem...")
extracted_text = ocr_pipeline(image)

# O resultado pode ser uma lista de dicionários.
# Para o Nanonets-OCR, o texto geralmente estará na chave 'text'.
if extracted_text and isinstance(extracted_text, list) and len(extracted_text) > 0:
    text_result = extracted_text[0].get('generated_text', '') # Alguns pipelines podem usar 'generated_text'
    if not text_result: # Se 'generated_text' não estiver presente, tente 'text'
        text_result = extracted_text[0].get('text', '')
    print("\n--- Texto Extraído ---")
    print(text_result)
else:
    print("Nenhum texto foi extraído da imagem.")

# 4. Processar o texto extraído para sua planilha Excel
# Aqui é onde a "mágica" acontece para o seu app.
# Você precisará de lógica para identificar os campos específicos (CNPJ, Valor, Data, etc.)
# no texto extraído e depois salvá-los em sua planilha Excel usando bibliotecas como 'pandas' ou 'openpyxl'.

print("\n--- Próximos Passos ---")
print("Agora, você precisará adicionar lógica para:")
print("1. Salvar as imagens de NFs localmente (se ainda não o faz).")
print("2. Iterar sobre as NFs e aplicar o OCR.")
print("3. Usar Expressões Regulares (Regex) ou outras técnicas de processamento de texto para extrair informações como CNPJ, valor, data, etc. (isso pode ser o mais desafiador).")
print("4. Armazenar os dados extraídos em uma estrutura (como um dicionário ou lista de dicionários).")
print("5. Exportar esses dados para uma planilha Excel usando bibliotecas como 'pandas' (DataFrame.to_excel()) ou 'openpyxl'.")