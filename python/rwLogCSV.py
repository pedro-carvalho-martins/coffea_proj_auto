from datetime import datetime
import csv
import json
import os

from shared_resource import file_lock

import rwSystemID

def writeCSV(tipo_registro, valor_venda_str, metodo_pag, etapa_erro, classe_erro, descricao_erro):

    classe_erro = classe_erro.replace('"','-')
    classe_erro = classe_erro.replace("'", "-")
    descricao_erro = descricao_erro.replace('"','-')
    descricao_erro = descricao_erro.replace("'", "-")

    # Obtains the datetime at the moment of the log register
    datetime_register_str = str(datetime.now())[0:19]

    # Obtains the name of the system (system ID)
    nome_sistema = rwSystemID.readSystemID()

    # Define the CSV filename
    filename_csv_tmp = "./log_files/tmp_log_client.csv"
    filename_csv_backup = "./log_files/backup_full_log_client.csv"

    # WRITE TO CSV TO BE PASSED TO SERVER
    with file_lock:
    # Open the file in append mode
        with open(filename_csv_tmp, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerow([datetime_register_str, nome_sistema, tipo_registro, valor_venda_str,
                                metodo_pag, etapa_erro, classe_erro[0:50], descricao_erro[0:100]])

    # WRITE TO BACKUP CSV - for TESTING PURPOSES ONLY
    with file_lock:
    # Open the file in append mode
        with open(filename_csv_backup, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerow([datetime_register_str, nome_sistema, tipo_registro, valor_venda_str,
                                metodo_pag, etapa_erro, classe_erro, descricao_erro])



def build_json_files_from_csv(client_datetime, server_datetime, max_lines_per_file=5):
    filename_csv_tmp_log = "./log_files/tmp_log_client.csv"
    json_filepath_folder = "./log_files/json_files_tmp/"
    client_name = rwSystemID.readSystemID()

    server_datetime_str = server_datetime.replace(":", "_")

    with file_lock:
        with open(filename_csv_tmp_log, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            rows = list(csvreader)

            part_num = 1

            for i in range(0, len(rows), max_lines_per_file):
                part_data = rows[i:i + max_lines_per_file]
                json_data = {
                    "client_datetime": str(client_datetime),
                    "server_datetime": str(server_datetime),
                    "data": []
                }

                for row in part_data:
                    json_data["data"].append(row)

                json_filename = f"{client_name}_{server_datetime_str}_part_{part_num}.json"
                json_filepath = os.path.join(json_filepath_folder, json_filename)
                with open(json_filepath, 'w') as jsonfile:
                    json.dump(json_data, jsonfile, indent=4)
                part_num += 1

        # Rows that haven't been passed to json files

        remaining_rows = rows[(part_num-1) * max_lines_per_file:]
        with open(filename_csv_tmp_log, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerows(remaining_rows)

    return json_filepath_folder