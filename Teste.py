import os

path = './PDFs'

for subpath in os.listdir(path): #Para 
    pdf_path = os.path.join(path, subpath)
lista_arquivos = os.listdir(pdf_path)
print(lista_arquivos)


'''    if os.path.isdir(caminho_pasta):
        print(caminho_pasta)
        print(f"Pasta: {subpath}")



        for arquivo in os.listdir(caminho_pasta):
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                print(caminho_arquivo)
                print(f"  Arquivo: {arquivo}")
'''



