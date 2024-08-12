import client_connection as servConn
import rwSystemID
import rwLogCSV
import os
import json
from datetime import datetime

def get_server_datetime():

    # Get system ID to be sent in request
    systemID = rwSystemID.readSystemID()

    try:
        request = {"type": "ping", "param1": systemID, "param2": 0}
        response_request_datetime_server = servConn.send_request(request)

    except Exception as e:
        print("Get server datetime failure")
        rwLogCSV.writeCSV("erro_outros", "", "", "request_datetime_server", str(e.__class__), str(e))
        response_request_datetime_server = {'ping': "erro", 'datetime_server': "erro"}

    server_datetime = response_request_datetime_server.get("datetime_server")
    return server_datetime

def get_client_datetime():
    datetime_register_str = str(datetime.now())[0:19]
    return datetime_register_str


def send_json_file(request):
    server_response = servConn.send_request(request)
    return server_response


def prep_send_json_files(json_folder):
    client_name = rwSystemID.readSystemID()

    # List all files in the specified folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    for json_file in json_files:
        # Construct the full file path
        file_path = os.path.join(json_folder, json_file)

        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            json_data = json.load(file)

        # Prepare the request
        request = {
            "type": "json_log_transmission",
            "param1": client_name,
            "param2": json_file,  # Use just the filename
            "param3": json_data
        }

        print("sending request for file " + json_file)

        print('request dict')
        print(request)

        # Send the request to server
        server_response = send_json_file(request)
        if server_response['status'] != 'received':
            return "fail"


def verify_json_files(json_folder):

    client_name = rwSystemID.readSystemID()

    # List all files in the specified folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    # For each file in the json files folder, ask the size to server, compare it to size in client
    # If the size is the same for that file name, delete the file from client

    for json_file in json_files:
        request = {
            "type": "verify_json_file_from_client",
            "param1": client_name,
            "param2": os.path.basename(json_file)
        }
        response_verify_json = servConn.send_request(request)

        print(os.path.basename(json_file))
        print('response verify json')
        print(response_verify_json)

        server_size = response_verify_json.get("file_size")

        if server_size == "error":
            return

        file_path = os.path.join(json_folder, json_file)
        client_size = os.path.getsize(file_path)

        print('client size')
        print(client_size)

        if server_size == client_size: # Not currently working. Investigate why.
        #if server_size > 0:
            request = {
                "type": "acknowledge_file",
                "param1": client_name,
                "param2": os.path.basename(json_file)
            }
            response_ack_json = servConn.send_request(request)

            if response_ack_json['ack'] == 'acknowledged':
                os.remove(json_file)
            else:
                print('error')


def startLogTransmission():

    client_datetime = get_client_datetime()
    server_datetime = get_server_datetime()

    if server_datetime == "erro":
        return

    json_files_folder_path = rwLogCSV.prepare_json_files_from_csv(client_datetime, server_datetime)

    # Call function to send files from json folder to server
    status_files_sending = prep_send_json_files(json_files_folder_path)

    if status_files_sending == 'fail':
        # Treat error later
        # can be a partial or full error. Go in depth later on.
        return

    ## Error treatment?? ##
    # what if a file with the same name already exists in the server? #
    # continue developing from here

    # Verifies if server has the files that have been passed and if the file sizes match, to erase json files from client

    verify_json_files(json_files_folder_path)


if __name__ == "__main__":
    startLogTransmission()
