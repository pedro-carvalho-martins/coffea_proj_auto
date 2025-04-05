
import os

# Global file path and default content
ultimo_pagamento_filename = './settings_files/ultimoPagamento.txt'
DEFAULT_ULTIMO_VALOR = "2.99"

def createUltimoPagamentoFile():
    """Creates ultimoPagamento.txt with the default value."""
    with open(ultimo_pagamento_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_ULTIMO_VALOR)
    print(f"{ultimo_pagamento_filename} created with default value: {DEFAULT_ULTIMO_VALOR.strip()}")

def readValue():
    print("readUltimoValor BEGINS")

    if not os.path.exists(ultimo_pagamento_filename):
        createUltimoPagamentoFile()

    with open(ultimo_pagamento_filename, "r", encoding='utf-8') as ultimoPagFile:
        ultimoValor = float(ultimoPagFile.readline().strip())

    print(ultimoValor)
    print("readUltimoValor ENDS")

    return ultimoValor

def writeValue(lastValue):
    outString = str(lastValue) + '\n'  # Ensures it writes with a newline at the end

    print(outString)

    with open(ultimo_pagamento_filename, "w", encoding='utf-8') as pMethodsFile:
        pMethodsFile.write(outString)


if __name__ == "__main__":
    readValue()

