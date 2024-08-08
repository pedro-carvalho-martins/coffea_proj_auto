from datetime import datetime
import csv

import rwSystemID

def writeCSV(tipo_registro, valor_venda_str, metodo_pag, etapa_erro, classe_erro, descricao_erro):

    # Obtains the datetime at the moment of the log register
    datetime_register_str = str(datetime.now())[0:19]

    # Obtains the name of the system (system ID)
    nome_sistema = rwSystemID.readSystemID()

    # Define the CSV filename
    filename = "./log_files/tmp_log_client.csv"

    # Open the file in append mode
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';')
        csvwriter.writerow([datetime_register_str, nome_sistema, tipo_registro, valor_venda_str,
                            metodo_pag, etapa_erro, classe_erro, descricao_erro])

