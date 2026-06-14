
####################################
## CLIENT SIDE (implement on Rpi) ##
####################################

import socket
import json
import time

import rwLogCSV


# Track repeated connection outages so we only log transitions.
_connection_outage_active = False
_connection_suppressed_count = 0
_connection_last_signature = None


def _connection_signature(exc):
    return f"{exc.__class__.__name__}:{getattr(exc, 'errno', None)}:{str(exc)}"


def _is_connection_issue(exc):
    return isinstance(exc, (socket.timeout, TimeoutError, ConnectionError, OSError))


def _log_connection_outage_once(exc):
    global _connection_outage_active
    global _connection_suppressed_count
    global _connection_last_signature

    signature = _connection_signature(exc)

    if not _connection_outage_active:
        rwLogCSV.writeCSV("erro_outros", "", "", "send_request_client_socket", str(exc.__class__), str(exc))
        _connection_outage_active = True
        _connection_suppressed_count = 0
        _connection_last_signature = signature
        return

    if signature == _connection_last_signature:
        _connection_suppressed_count += 1
        return

    rwLogCSV.writeCSV("erro_outros", "", "", "send_request_client_socket", str(exc.__class__), str(exc))
    _connection_suppressed_count += 1
    _connection_last_signature = signature


def _log_connection_recovery():
    global _connection_outage_active
    global _connection_suppressed_count
    global _connection_last_signature

    if _connection_outage_active:
        if _connection_suppressed_count > 0:
            rwLogCSV.writeCSV(
                "erro_outros",
                "",
                "",
                "send_request",
                "",
                f"connection restored after suppressing {_connection_suppressed_count} repeated connection failures"
            )

        _connection_outage_active = False
        _connection_suppressed_count = 0
        _connection_last_signature = None


# Function to send requests to the server
def send_request(request, max_retries=3, delay=2, timeout=5):
    server_ip = '18.230.15.249'  # Server's Elastic IP address (AWS)
    server_port = 8080  # Server's port number

    attempt = 0

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
                _log_connection_recovery()
                return response

        except Exception as e:
            if _is_connection_issue(e):
                _log_connection_outage_once(e)
            else:
                rwLogCSV.writeCSV("erro_outros", "", "", "send_request_client_socket", str(e.__class__), str(e))
            print("Exception raised")

        attempt += 1
        time.sleep(delay)

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
