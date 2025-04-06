import datetime
import csv
import json
import os
import shutil

from shared_resource import file_lock

import rwSystemID
import rwSystemVersion


def delete_old_csv_backup_files():
    # Get the current year
    current_year = datetime.datetime.now().year

    # Get all CSV files in the backup directory
    csv_files = [f for f in os.listdir('./log_files/csv_full_logs_backup/') if f.endswith('.csv')]

    for csv_file in csv_files:
        if csv_file.startswith('backup_full_client_log_Y'):
            # Extract the year from the file name
            year = int(csv_file[24:28])

            # If the file is older than last year, delete it
            if year < current_year - 1:
                os.remove(os.path.join('./log_files/csv_full_logs_backup/', csv_file))
                print(f"Deleted old backup CSV file: {csv_file}")


def prepare_and_check_current_year_week_backup_csv_path():

    datetime_now_isocalendar = datetime.datetime.now().isocalendar()
    year_week_string = 'Y' + str(datetime_now_isocalendar[0]) + '_W' + str(datetime_now_isocalendar[1]).zfill(2)

    current_yearweek_csv_file_path = "./log_files/csv_full_logs_backup/backup_full_client_log_" + year_week_string + ".csv"

    # Check if the CSV file exists
    if not os.path.isfile(current_yearweek_csv_file_path):

        # Define the model CSV file path
        model_csv_path = "./log_files/log_header_backup_model.csv"

        # Check if the model CSV file exists
        if os.path.isfile(model_csv_path):
            # Copy the model CSV file to the specified path
            shutil.copyfile(model_csv_path, current_yearweek_csv_file_path)
            print(f"'{current_yearweek_csv_file_path}' created from '{model_csv_path}'.")

            # Delete old backup files
            delete_old_csv_backup_files()

        else:
            print(f"Model CSV file '{model_csv_path}' does not exist.")
            # Error treatment pending

    return current_yearweek_csv_file_path



def writeCSV(tipo_registro, valor_venda_str, metodo_pag, etapa_erro, classe_erro, descricao_erro):

    classe_erro = classe_erro.replace('"','-')
    classe_erro = classe_erro.replace("'", "-")
    descricao_erro = descricao_erro.replace('"','-')
    descricao_erro = descricao_erro.replace("'", "-")

    # Obtains the datetime at the moment of the log register
    datetime_register_str = str(datetime.datetime.now())[0:19]

    # Obtains the name of the system (system ID)
    nome_sistema = rwSystemID.readSystemID()
    versao_sistema = rwSystemVersion.readVersion()

    # Define the CSV filename
    filename_csv_tmp = "./log_files/tmp_log_client.csv"
    model_csv_path = "./log_files/log_header_backup_model.csv"

    # Create tmp_log_client.csv from model if it doesn't exist
    if not os.path.isfile(filename_csv_tmp):
        if os.path.isfile(model_csv_path):
            shutil.copyfile(model_csv_path, filename_csv_tmp)
            print(f"'{filename_csv_tmp}' created from '{model_csv_path}'.")
        else:
            print(f"Model file '{model_csv_path}' not found. Cannot create '{filename_csv_tmp}'.")
            return  # Exit early if the model is missing

    # WRITE TO CSV TO BE PASSED TO SERVER
    with file_lock:
    # Open the file in append mode
        with open(filename_csv_tmp, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerow([datetime_register_str, nome_sistema, tipo_registro, valor_venda_str,
                                metodo_pag, etapa_erro, classe_erro[0:50], descricao_erro[0:100], versao_sistema])


    # WRITE TO BACKUP CSV

    filename_csv_backup = prepare_and_check_current_year_week_backup_csv_path()

    with file_lock:
    # Open the file in append mode
        with open(filename_csv_backup, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerow([datetime_register_str, nome_sistema, tipo_registro, valor_venda_str,
                                metodo_pag, etapa_erro, classe_erro, descricao_erro, versao_sistema])


def remove_corrupted_characters(file_path, temp_file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    # Remove null characters
    cleaned_content = content.replace(b'\x00', b'')
    # Write cleaned content to a temporary file
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(cleaned_content)

def clean_csv_file(csv_file_path):
    temp_file_path = csv_file_path + '.tmp'

    # Lock file to prevent simultaneous access
    with file_lock:
        # Remove null characters and create a temporary file
        remove_corrupted_characters(csv_file_path, temp_file_path)

        # Process the cleaned CSV file
        with open(temp_file_path, 'r', encoding='utf-8', errors='replace') as file:
            reader = csv.reader(file, delimiter=';')
            rows = [row for row in reader]

        # Write the cleaned content back to the original file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(rows)

        # Remove the temporary file
        os.remove(temp_file_path)


def build_json_files_from_csv(client_datetime, server_datetime, max_lines_per_file=5):
    filename_csv_tmp_log = "./log_files/tmp_log_client.csv"
    json_filepath_folder = "./log_files/json_files_tmp/"
    client_name = rwSystemID.readSystemID()

    server_datetime_str = server_datetime.replace(":", "_")

    # Cleans the CSV file, since many issues with corrupted characters in this file started to arise
    clean_csv_file("./log_files/tmp_log_client.csv")

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

        # Ensure that the header is retained
        if len(rows) > 0:
            header = rows[0]  # Assuming the first row is the header
            remaining_rows.insert(0, header)

        with open(filename_csv_tmp_log, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            csvwriter.writerows(remaining_rows)

    return

# Define the CSV filename
filename_csv_tmp = "./log_files/tmp_log_client.csv"
model_csv_path = "./log_files/log_header_backup_model.csv"

# Create tmp_log_client.csv from model if it doesn't exist
if not os.path.isfile(filename_csv_tmp):
    if os.path.isfile(model_csv_path):
        shutil.copyfile(model_csv_path, filename_csv_tmp)
        print(f"'{filename_csv_tmp}' created from '{model_csv_path}'.")
    else:
        print(f"Model file '{model_csv_path}' not found. Cannot create '{filename_csv_tmp}'.")