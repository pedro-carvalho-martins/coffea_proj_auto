import json
import socket
import time
import rwLogCSV  # ✅ Keep Original CSV Logging
from logger import logger  # ✅ New system logging

def send_request(request, max_retries=3, delay=2, timeout=5):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(timeout)

    server_ip = '18.230.15.249'
    server_port = 8080
    attempt = 0
    response = None  # ✅ Prevents UnboundLocalError

    while attempt < max_retries:
        try:
            logger.info(f"Connecting to server at {server_ip}:{server_port}, Attempt {attempt + 1}")
            client_socket.connect((server_ip, server_port))
            logger.debug(f"Connected successfully. Sending request: {json.dumps(request)}")

            client_socket.send(json.dumps(request).encode())
            response = client_socket.recv(1024).decode()
            response = json.loads(response)

            logger.debug(f"Response received: {response}")
            return response  # ✅ Ensures response is always returned

        except Exception as e:
            logger.error(f"Error during send_request (Attempt {attempt + 1}): {e}")
            rwLogCSV.writeCSV("erro_outros", "", "", "send_request", str(e.__class__), str(e))  # ✅ Keep Original CSV Logging
            response = {"error": "Request failed"}  # ✅ Prevents UnboundLocalError

        finally:
            client_socket.close()

        attempt += 1
        time.sleep(delay)

    logger.error(f"Max retries exceeded. Could not connect to server.")
    rwLogCSV.writeCSV("erro_outros", "", "", "send_request", "MaxRetriesExceeded", "Could not connect to server")  # ✅ Keep Original CSV Logging
    return response  # ✅ Ensures a valid response is always returned
