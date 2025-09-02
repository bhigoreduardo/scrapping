import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API URLs
    B3_API_BASE_URL = os.getenv("B3_API_BASE_URL")
    RECEITAWS_BASE_URL = os.getenv("RECEITAWS_BASE_URL")
    BRASIL_API_BASE_URL = os.getenv("BRASIL_API_BASE_URL")

    # App Configs
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CACHE_DIR = os.path.join(DATA_DIR, "cache")


settings = Settings()
