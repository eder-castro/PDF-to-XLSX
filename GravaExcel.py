import pandas as pd
from datetime import datetime
import xlsxwriter
from dateutil import parser

# Nome do arquivo Excel que você quer usar
NOME_ARQUIVO_EXCEL = "CONTROLE FLUXO ORIGINAL.xlsx"

pasta_nfs = './'
#lista_arquivos = os.listdir(pasta_nfs)
qt_arquivos_plan = 0
colunas = ["NF", "Data NF", "CNPJ", "CNPJ/CPF Tomador", "Contrato", "Pedido", "Valor NF", "Nome do Arquivo"]
novos_valores = []

lista_de_dicionarios = [{'Numero_Nota': '36501', 'Data_Emissao': '01/08/2023', 'CNPJ_Prestador': '07601279000108', 'CNPJ_Tomador': '01666851868', 'Pedido': '', 'Contrato': '', 'Valor_Total': '900,00', 'Nome_Arquivo': '08 - ANGRA DOS REIS - NF 36501.pdf'},
{'Numero_Nota': '1521', 'Data_Emissao': '19/05/2025', 'CNPJ_Prestador': '12599272000139', 'CNPJ_Tomador': '13718634000126', 'Pedido': '4500012167', 'Contrato': '4700000307', 'Valor_Total': '548,33', 'Nome_Arquivo': '1521 Icon.pdf'},
{'Numero_Nota': '1735', 'Data_Emissao': '20/05/2025', 'CNPJ_Prestador': '59291534000167', 'CNPJ_Tomador': '04553060000192', 'Pedido': '4500012196', 'Contrato': '4700000341', 'Valor_Total': '2.590,09', 'Nome_Arquivo': '1735 NF - ICON - VSERRA.pdf'}]

def parse_data_emissao(data_str):
    try:
        dt = parser.parse(data_str)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception:
        try:
            return datetime.strptime(data_str, "%d/%m/%Y")
        except Exception:
            print(f"[AVISO] Data inválida ignorada: {data_str}")
            return None

def formatar_valor(chave, valor):
    if chave == "Data_Emissao":
        # Exemplo: formatar para ISO
        return parse_data_emissao(valor) if valor else valor
    elif chave == "Nome_Arquivo":
        return valor
    elif chave == "Valor_Total":
        return float(valor.replace(",", ".")) if isinstance(valor, str) else float(valor)
    else:
        return int(valor) if valor and valor.isdigit() else valor

try:
    df_existente = pd.read_excel(NOME_ARQUIVO_EXCEL, sheet_name='#NFs#', header=1)
    print(df_existente.columns)
except FileNotFoundError:
    df_existente = pd.DataFrame(columns=colunas)

for dicionario in lista_de_dicionarios:
    if dicionario:
        existe = ((df_existente['NF'] == dicionario['Numero_Nota']) &
                    (df_existente['CNPJ'] == dicionario['CNPJ_Prestador'])).any()
        if not existe:
            novos_valores.append(dicionario)
            print("NF Incluída: ", dicionario)
            qt_arquivos_plan += 1
        else:
            print(f"[AVISO] NF {dicionario['Numero_Nota']} do CNPJ {dicionario['CNPJ_Prestador']} já existe na planilha.")
    else:
        print(f"Erro na leitura do dicionario")


if novos_valores:
    df_novos = pd.DataFrame(novos_valores)
    df_final = pd.concat([df_existente, df_novos], ignore_index=True)
else:
    df_final = df_existente

# Usando xlsxwriter para formatação
with pd.ExcelWriter(NOME_ARQUIVO_EXCEL, engine="xlsxwriter") as writer:
    df_final.to_excel(writer, sheet_name='#NFs#', startrow=1, index=False, header=False)

    workbook = writer.book
    worksheet = writer.sheets['#NFs#']

    # Escreve os dados com o formato das células e formatos específicos das colunas
    for row_num, row_data in df_final.iterrows():
        for col_num, value in enumerate(row_data):
            if pd.isna(value):
                worksheet.write(row_num + 1, col_num, "")#, cell_format)
            else:
                column_name = df_final.columns[col_num]
                if column_name == "NF":
                    worksheet.write_number(row_num + 1, col_num, value)#, number_format)
                elif column_name == "Data NF":
                    if isinstance(value, datetime):
                        worksheet.write_datetime(row_num + 1, col_num, value)#, date_format)
                    else:
                        worksheet.write(row_num + 1, col_num, "")#, cell_format)
                elif column_name == "CNPJ":
                    if pd.notna(value):
                        str_value = str(int(value)) if isinstance(value, (int, float)) else str(value)
                        if len(str_value) == 11:
                            worksheet.write_number(row_num + 1, col_num, int(value))#, cpf_format)
                        else:
                            worksheet.write_number(row_num + 1, col_num, value)#, cnpj_format)
                elif column_name == "CNPJ/CPF Tomador":
                    if pd.notna(value):
                        str_value = str(int(value)) if isinstance(value, (int, float)) else str(value)
                        if len(str_value) == 11:
                            worksheet.write_number(row_num + 1, col_num, int(value))#, cpf_format)
                        else:
                            worksheet.write_number(row_num + 1, col_num, value)#, cnpj_format)
                    else:
                        worksheet.write(row_num + 1, col_num, "")#, cell_format)
                elif column_name == "Valor NF":
                    worksheet.write_number(row_num + 1, col_num, value)#, valor_format)
                else:
                    worksheet.write(row_num + 1, col_num, value)#, cell_format)
