
####################################
## CLIENT SIDE (implement on Rpi) ##
####################################

import socket
import json
import time


# Function to send requests to the server
def send_request(request):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    server_ip = '127.0.0.1'  # Replace with the server's IP address
    server_port = 8080  # Replace with the server's port number
    client_socket.connect((server_ip, server_port))

    try:
        # Send request to the server
        client_socket.send(json.dumps(request).encode())

        # Receive response from the server
        response = client_socket.recv(1024).decode()
        response = json.loads(response)
        print("Response from server:", response)
    finally:
        # Close the socket
        client_socket.close()

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
