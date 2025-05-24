import re

texto_teste = "ELETRÔNICA\nNº:2025/92Emitida em:\n19/05/2025 às 07:04:57"

# Tentativa 1: mais flexível para o "Nº"
match1 = re.search(r"[Nn][º°.:#]?\s*(\d+/\d+)", texto_teste, re.DOTALL)
if match1:
    print(f"Match 1 encontrado: {match1.group(1)}")
else:
    print("Match 1 NÃO encontrado.")

# Tentativa 2: mais explícita para o prefixo
match2 = re.search(r"N[º°]?:\s*(\d+/\d+)", texto_teste, re.DOTALL)
if match2:
    print(f"Match 2 encontrado: {match2.group(1)}")
else:
    print("Match 2 NÃO encontrado.")

# Tentativa 3: caso o 'º' seja realmente o caracter unicode quebrado
# Você pode copiar e colar o 'º' direto do seu texto de origem aqui.
# Substitua o 'º' abaixo pelo que você tem no seu texto se for diferente.
match3 = re.search(r"Nº:\s*(\d+/\d+)", texto_teste, re.DOTALL) # Copie e cole o 'º' do seu texto
if match3:
    print(f"Match 3 encontrado: {match3.group(1)}")
else:
    print("Match 3 NÃO encontrado.")

# Tentativa 4: O mais genérico possível para o prefixo
match4 = re.search(r"(?:Nº|N|No|Nro)\s*[:\.]?\s*(\d+/\d+)", texto_teste, re.DOTALL)
if match4:
    print(f"Match 4 encontrado: {match4.group(1)}")
else:
    print("Match 4 NÃO encontrado.")