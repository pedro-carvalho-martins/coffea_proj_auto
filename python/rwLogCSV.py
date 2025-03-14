import os
import shutil
import datetime
import rwLogCSV  # ✅ Keep Original CSV Logging
from logger import logger  # ✅ New system logging
from shared_resource import file_lock  # ✅ Prevent race conditions

def prepare_and_check_current_year_week_csv_path():
    with file_lock:  # ✅ Ensures only one thread creates the log file at a time
        logger.info("Checking or creating weekly log file...")

        datetime_now_isocalendar = datetime.datetime.now().isocalendar()
        year_week_string = 'Y' + str(datetime_now_isocalendar[0]) + '_W' + str(datetime_now_isocalendar[1]).zfill(2)
        current_yearweek_csv_file_path = f"./log_files/csv_full_logs_backup/backup_full_client_log_{year_week_string}.csv"

        if not os.path.isfile(current_yearweek_csv_file_path):
            model_csv_path = "./log_files/log_header_backup_model.csv"

            if os.path.isfile(model_csv_path):
                shutil.copyfile(model_csv_path, current_yearweek_csv_file_path)
                logger.info(f"Weekly log file created from model: {current_yearweek_csv_file_path}")
            else:
                logger.error(f"Model CSV file '{model_csv_path}' is missing! Returning error.")
                rwLogCSV.writeCSV("erro_outros", "", "", "prepare_and_check_log", "ModelFileMissing", "Model CSV not found")  # ✅ Keep Original CSV Logging
                return "LOG_FILE_CREATION_ERROR"

        logger.debug(f"Weekly log file path confirmed: {current_yearweek_csv_file_path}")
        return current_yearweek_csv_file_path
