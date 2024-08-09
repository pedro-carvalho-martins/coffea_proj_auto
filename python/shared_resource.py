# file: shared_resource.py
import threading

# Create a lock object in a shared module
file_lock = threading.Lock()