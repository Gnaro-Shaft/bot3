import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        return logger  # Évite d'ajouter plusieurs fois les handlers

    # Formatter commun
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handler fichier
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"), maxBytes=1_000_000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Ajout des handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
