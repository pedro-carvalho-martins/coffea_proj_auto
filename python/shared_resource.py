# file: shared_resource.py
import threading

# Create a lock object in a shared module
file_lock = threading.Lock()
gpio_lock = threading.Lock()
gpio_listener_pause = threading.Event()
