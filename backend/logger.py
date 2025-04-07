# backend/logger.py

import logging
import sys

logger = logging.getLogger("     GUIComparator")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# FastAPI/uvicorn logging integration
logging.basicConfig(level=logging.INFO)
