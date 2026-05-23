import logging
import sys

# Configure a clean formatter for the console output
# format: 2026-05-24 01:31:01 [INFO] Message
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Set up the console handler pointing to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Clear existing handlers to avoid duplicate output on re-imports
if root_logger.hasHandlers():
    root_logger.handlers.clear()

root_logger.addHandler(console_handler)

# Suppress noisy external library logs
for logger_name in ["google", "google_genai", "google.genai", "httpx", "httpcore", "urllib3"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger("closira")
