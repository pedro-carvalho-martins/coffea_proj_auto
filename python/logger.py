import logging
import os

# Create logs directory if it does not exist
log_directory = "./logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "debug.log")),  # General debugging
        logging.FileHandler(os.path.join(log_directory, "errors.log")),  # Errors only
    ]
)

logger = logging.getLogger(__name__)
