import os

pasta_nfs = './PDFs'
for subpasta in os.listdir(pasta_nfs):
    print("Pasta --------------", pasta_nfs)
    print("Subpasta -----------", subpasta)
    pasta_e_subpasta_nfs = os.path.join(pasta_nfs, subpasta)
    print("Pasta + Subpasta", pasta_e_subpasta_nfs)
    lista_arquivos = os.listdir(pasta_e_subpasta_nfs)
    print("arquivos na pasta", lista_arquivos)
    # Para cada arquivo na lista de arquivos
    for arquivo in lista_arquivos:
        if arquivo.lower().endswith(".pdf"):
            #caminho_completo_pdf = os.path.join(pasta_e_subpasta_nfs, arquivo)
            print(arquivo)


