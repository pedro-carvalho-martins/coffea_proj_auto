
####################################
## CLIENT SIDE (implement on Rpi) ##
####################################

import socket
import json
import time

from python import rwLogCSV


# Function to send requests to the server
def send_request(request, max_retries=3, delay=2, timeout=5):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set a timeout for the socket operations (in seconds)
    client_socket.settimeout(timeout)

    # Connect to the server
    server_ip = '18.230.15.249'  # Server's Elastic IP address (AWS)
    server_port = 8080  # Server's port number

    attempt = 0
    while attempt < max_retries:

        try:
            client_socket.connect((server_ip, server_port))

            try:
                # Send request to the server
                client_socket.send(json.dumps(request).encode())

                # Receive response from the server
                response = client_socket.recv(1024).decode()
                response = json.loads(response)
                print("Response from server:", response)
                break # If it succeeds, exits the loop (break executes 'finally' before exiting)


            except Exception as e:

                rwLogCSV.writeCSV("erro_outros", "", "", "send_request", str(e.__class__), str(e))

                print("Exception raised")

            finally:
                # Close the socket
                client_socket.close()

        except Exception as e:

            rwLogCSV.writeCSV("erro_outros", "", "", "send_request_client_socket", str(e.__class__), str(e))

            print("Exception raised")

        attempt += 1
        time.sleep(delay)

    if (attempt == max_retries):
        rwLogCSV.writeCSV("erro_outros", "", "", "send_request", "", "maximum number of attempts to connect to server exceeded")

    return response

# # Example usage: Send "create_pix" request
# request_create_pix = {"type": "create_pix", "param1": 10, "param2": 20}
# print(send_request(request_create_pix))
#
# time.sleep(1)
#
# # Example usage: Send "cob_read" request (placeholder)
# request_cob_read = {"type": "cob_read", "param1": 30, "param2": 'wg8v0y8kpavzzjwol8idxgs9z7qlpajj4tn'}
# print(send_request(request_cob_read))
#
# time.sleep(1)
#
# # Example usage: Send "auth_rpi" request (placeholder)
# request_auth_rpi = {"type": "auth_rpi", "param1": 50, "param2": 60}
# send_request(request_auth_rpi)
#
# # Example usage: Send "telemetry_get" request (placeholder)
# request_telemetry_get = {"type": "telemetry_get", "param1": 70, "param2": 80}
# send_request(request_telemetry_get)

if __name__ == "__main__":
    pass
