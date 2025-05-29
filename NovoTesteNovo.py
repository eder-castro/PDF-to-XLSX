import os

pasta_PDFs = './PDFs'

def PDF_selec(caminho_arquivo):
    """
    Esta função será chamada para processar um arquivo individualmente.
    Adicione sua lógica de processamento principal aqui.
    Deve retornar True se o processamento foi bem-sucedido e False caso contrário.
    """
    print(f"  Chama função PDF_Selec para: {caminho_arquivo}")
    # Exemplo: Simula que alguns arquivos são processados com sucesso e outros não
    if "falha" in caminho_arquivo.lower():
        return False
    return True

def processar_arquivo_secundario(caminho_arquivo):
    """
    Esta função será chamada para arquivos que não foram processados pela função principal.
    Adicione sua lógica de processamento secundário aqui.
    """
    print(f"  Chama função PDF_img para: {caminho_arquivo}")

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
        for sub_item in itens_na_subpasta:
            caminho_completo_sub_item = os.path.join(caminho_completo_item, sub_item)
            if os.path.isdir(caminho_completo_sub_item):
                subpastas_contadas += 1
            else:
                arquivos_contados += 1
                # Tenta processar o arquivo com a função principal
                if not PDF_selec(caminho_completo_sub_item):
                    arquivos_nao_processados.append(caminho_completo_sub_item)
        print(f"Total de pastas em {nome_subpasta} = {subpastas_contadas}")
        print(f"Total de arquivos em {nome_subpasta} = {arquivos_contados}")
        # Após tentar processar todos os arquivos da pasta com a função principal,
        # itera sobre os que não foram processados para a função secundária.
        if arquivos_nao_processados:
            print(f"\n--- Reprocessando arquivos em {nome_subpasta} que não foram processados inicialmente ---")
            for arquivo_reprocessar in arquivos_nao_processados:
                processar_arquivo_secundario(arquivo_reprocessar)
        else:
            print(f"\nTodos os arquivos em {nome_subpasta} foram processados pela função PDF_selec.")
        print(f"--- Saindo da subpasta: {nome_subpasta} ---")