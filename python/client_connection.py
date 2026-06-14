
####################################
## CLIENT SIDE (implement on Rpi) ##
####################################

import socket
import json
import time

import rwLogCSV


# Function to send requests to the server
def send_request(request, max_retries=3, delay=2, timeout=5):
    server_ip = '18.230.15.249'  # Server's Elastic IP address (AWS)
    server_port = 8080  # Server's port number

    attempt = 0
    response = None

    while attempt < max_retries:
        try:
            # Open a fresh socket for each attempt so failed retries do not reuse a bad connection.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(timeout)
                client_socket.connect((server_ip, server_port))

                # Send request to the server
                client_socket.sendall(json.dumps(request).encode())

                # Receive response from the server
                response_text = client_socket.recv(1024).decode()
                response = json.loads(response_text)
                print("Response from server:", response)
                return response

        except Exception as e:
            rwLogCSV.writeCSV("erro_outros", "", "", "send_request_client_socket", str(e.__class__), str(e))
            print("Exception raised")

        attempt += 1
        time.sleep(delay)

    if attempt == max_retries:
        rwLogCSV.writeCSV("erro_outros", "", "", "send_request", "", "maximum number of attempts to connect to server exceeded")

    raise ConnectionError("maximum number of attempts to connect to server exceeded")

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
