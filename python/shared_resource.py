# file: shared_resource.py
import threading

# Create a lock object in a shared module
file_lock = threading.Lock()
gpio_lock = threading.Lock()
gpio_listener_pause = threading.Event()
customer_interaction_active = threading.Event()
remote_command_gate_lock = threading.Lock()
background_connection_check_lock = threading.Lock()
factory_reset_in_progress = threading.Event()
server_sync_lock = threading.Lock()


def set_customer_interaction_active(active):
    with remote_command_gate_lock:
        if active:
            customer_interaction_active.set()
        else:
            customer_interaction_active.clear()
